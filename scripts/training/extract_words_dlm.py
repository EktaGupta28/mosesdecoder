#!/usr/bin/env python3.4

"""
NAME
    extract_words_dlm.py -- extract samples for DLM training

SYNOPSIS

    extract_words_dlm.py SOURCE TARGET ALIGN > OUT
 

DESCRIPTION
    Given aligments for source and target sentences, outputs examples for 
    discriminative lexicon model training. Every target word (even unaligned 
    one) is output with following information:

    - Sentence ID;
    - Space delimited source spans, e.g. "0-2 3-4" means "0,1,3";
    - Start of target span; 
    - End of target span.
   
    Spans are defined using numbering of positions between words (starting from 
    zero -- position before the first word).

    Output is written to stdout.

PARAMETERS
    SOURCE
        filename of file with tokenized (space-delimited) source sentences, 
        one per line

    TARGET
        path to file with tokenized target sentences

    ALIGN
        path to file with combined alignments 
"""

import collections
import fileinput
import itertools
import sys

# ------------------------------------------------------- Parsing input files --

def parse_sentence(sentence_line):
    tokens = sentence_line.strip().split(" ")
    return tokens

def parse_alignment_pairs(align_line):
    align_line = align_line.strip()
    if not align_line:
        return []

    pairs = [pair.split("-") for pair in align_line.split(" ")]
    return [(int(pair[0]), int(pair[1])) for pair in pairs]

# ---------------------------------------------------------------- Extraction --

def cept_to_spans(cept):
    SPANS = []
    for index in sorted(cept):
        if not SPANS:
            SPANS.append([index, index + 1])
            continue
        if SPANS[-1][1] == index:
            SPANS[-1][1] = index + 1
        else:
            SPANS.append([index, index + 1])

    return SPANS

def spans_to_string(spans):
    return " ".join("-".join(map(str, span)) for span in spans)

SENTENCE_ID = 1

def extract_from_sentence(source, target, align_pairs):
    global SENTENCE_ID

    source_cept = collections.defaultdict(lambda: [])
    for pair in align_pairs:
        source_cept[pair[1]].append(pair[0])

    last_aligned_position = 0

    for target_index in range(len(target)):
        cept = source_cept[target_index]
        spans = None if not cept else cept_to_spans(cept)

        if not cept:
            spans = [[last_aligned_position, last_aligned_position]]
        else:
            last_aligned_position = max(cept) + 1

        params = (
            SENTENCE_ID,
            spans_to_string(spans),
            target_index,
            target_index + 1,
            " ".join(source[index] for index in cept),
            target[target_index]
        )

        print("%i\t%s\t%i\t%i\t%s\t%s" % (params))

    SENTENCE_ID += 1

def extract_all(source_path, target_path, align_path):
    input_files = itertools.zip_longest(
        fileinput.input(source_path), 
        fileinput.input(target_path), 
        fileinput.input(align_path)
    ) 

    for source_line, target_line, align_line in input_files:
        if source_line is None or target_line is None or align_line is None:
            msg = "Source, target and align files have different # of lines"
            raise Exception(msg)

        source_sentence = parse_sentence(source_line)
        target_sentence = parse_sentence(target_line)
        align_pairs = parse_alignment_pairs(align_line)

        extract_from_sentence(source_sentence, target_sentence, align_pairs)

# ---------------------------------------------------------------------- Main --

def main():
    extract_all(sys.argv[1], sys.argv[2], sys.argv[3])

if __name__ == "__main__":
    main()