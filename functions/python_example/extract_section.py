#!/usr/bin/env python

import csv
import os
import re


class ExtractSection(object):

    FDA_LABELING_NEW_FORMAT = 'HIGHLIGHTS OF PRESCRIBING INFORMATION'

    FDA_OLD_LABELING_CLINICAL_STUDIES_PARENT_START = 'CLINICAL PHARMACOLOGY'
    FDA_OLD_LABELING_CLINICAL_STUDIES_START = 'CLINICAL STUDIES'
    FDA_OLD_LABELING_CLINICAL_STUDIES_END = 'INDICATIONS'

    FDA_NEW_LABELING_CLINICAL_STUDIES_START = '14 CLINICAL STUDIES'
    FDA_NEW_LABELING_CLINICAL_STUDIES_END = '15 REFERENCES'

    def __init__(self, lines):
        self.lines = lines
    
    def extract_clinical_studies(self):
        ## check if the document is old or new
        is_new = True if self.FDA_LABELING_NEW_FORMAT in self.lines[0] else False
        
        try:
            section_text = ''
            if is_new:
                section_text += self.extract_text_new_labeling_doc()
            else:
                section_text += self.extract_text_old_labeling_doc()
                
        except Exception as ex:
            raise Exception("Failed to extract text", ex)

        return section_text

    ## Helpers
    def extract_text_new_labeling_doc(self):
        section_start = self.FDA_NEW_LABELING_CLINICAL_STUDIES_START
        section_end = self.FDA_NEW_LABELING_CLINICAL_STUDIES_END

        extract_lines = []
        started_extracting = False
        first_match = True

        section_start_words = list(map(str.lower, self.extract_words_from_sentence(section_start)))
        section_end_words = list(map(str.lower, self.extract_words_from_sentence(section_end)))

        for  line in self.lines:
            if section_start.lower() in line.lower():
                words = self.extract_words_from_sentence(line)
                words = list(map(str.lower, words))
                
                if set(words).intersection(set(section_start_words)) == set(section_start_words):
                    # table of contents match, ignore
                    if first_match:
                        first_match = False
                        continue

                    started_extracting = True
                    extract_lines.append(line)

            if started_extracting:
                ## look for the end
                if section_end.lower() in line.lower():
                    words = self.extract_words_from_sentence(line)
                    words = list(map(str.lower, words))
                    if set(words).intersection(set(section_end_words)) == set(section_end_words):
                        started_extracting = False
                        break
                else:
                    extract_lines.append(line)

        return "".join(extract_lines)

    def extract_text_old_labeling_doc(self):
        txt = "".join(self.lines)

        extract_lines = []
        started_extracting = False
        
        section_start = "^" + self.FDA_OLD_LABELING_CLINICAL_STUDIES_START

        ## start, match second occurence
        for line in self.lines:
            if self.FDA_OLD_LABELING_CLINICAL_STUDIES_START.lower() in line.lower():
                words = [w for w in line.split() if w.lower().startswith("c") or w.lower().startswith("s")]
                if len(words) == 2:
                    extract_lines.append(line)
                    started_extracting = True

            ## Look for end pattern
            if started_extracting:
                ## either indication or indications and usage section is present
                if re.search("^INDICATIONS", line, re.I) is not None:
                    started_extracting = False
                    break
                elif re.search("^INDICATIONS AND USAGE", line, re.I) is not None:
                    started_extracting = False
                    break
                else:
                    extract_lines.append(line)
        
        return "".join(extract_lines)

    def extract_words_from_sentence(self,str):
        res = re.findall(r'\w+', str)
        return res
