#!/usr/bin/env python
import csv
import os
import sys
import argparse

# if you move this script, you'll need to change this method of getting the imports
partis_dir = os.path.dirname(os.path.realpath(__file__)).replace('/bin', '')
sys.path.insert(1, partis_dir + '/python')

import utils
import glutils
from clusterpath import ClusterPath

parser = argparse.ArgumentParser()
parser.add_argument('--fname', default=partis_dir + '/test/reference-results/partition-ref-simu.yaml')
args = parser.parse_args()

glfo, annotation_list, partition_lines = utils.read_yaml_output(args.fname)
annotations = {':'.join(adict['unique_ids']) : adict for adict in annotation_list}  # collect the annotations in a dictionary so they're easier to access

if len(partition_lines) == 0:
    print 'no partitions read from %s' % args.fname
else:
    print utils.color('green', 'list of partitions:')
    cpath = ClusterPath(partition_lines=partition_lines)
    cpath.print_partitions(abbreviate=True)  # 'abbreviate' print little 'o's instead of the full sequence ids

# print annotations for the biggest cluster in the most likely partition
most_likely_partition = cpath.partitions[cpath.i_best]  # a partition is represented as a list of lists of strings, with each string a sequence id
sorted_clusters = sorted(most_likely_partition, key=len, reverse=True)
print '\n%s' % utils.color('green', 'annotation for the biggest cluster:')
for cluster in sorted_clusters:
    cluster_annotation = annotations[':'.join(cluster)]
    utils.print_reco_event(cluster_annotation)
    break

# print '\n\n%s' % utils.color('green', 'available keys:')
# for key, val in cluster_annotation.items():
#     print '%20s %s' % (key, val)


# for old csv files:
# parser.add_argument('--annotation-file', default=partis_dir + '/test/reference-results/annotate-ref-simu.csv')
# parser.add_argument('--germline-info-dir', default=partis_dir + '/test/reference-results/test/parameters/simu/hmm/germline-sets')
# parser.add_argument('--locus', default='igh')
# glfo = glutils.read_glfo(args.germline_info_dir, locus=args.locus)  # read germline info (it'll be nice to switch to yaml output files so we can store this in the same file as the rest of the output)
# with open(args.annotation_file) as csvfile:
#     reader = csv.DictReader(csvfile)
#     for line in reader:  # one line for each annotation
#         if line['v_gene'] == '':  # failed (i.e. couldn't find an annotation)
#             continue
#         utils.process_input_line(line)  # converts strings in the csv file to floats/ints/dicts/etc.
#         utils.add_implicit_info(glfo, line)  # add stuff to <line> that's useful, but isn't written to the csv since it's redundant
#         print 'print one annotation, then break:'
#         utils.print_reco_event(line)  # print ascii-art representation of the rearrangement event
#         print '\n\navailable keys:'
#         for key, val in line.items():
#             print '%20s %s' % (key, val)
#         break