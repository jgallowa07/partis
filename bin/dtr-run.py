#!/usr/bin/env python
import sys
import colored_traceback.always
import os
import yaml
import argparse
import numpy

sys.path.insert(1, './python')
import utils
import treeutils

# NOTE not just to run dtr, also to run other non-lb metrics
# also note, this only really works on simulation, although it maybe wouldn't take much work to get it working on data

parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('--infname', required=True)
parser.add_argument('--base-plotdir', required=True)
parser.add_argument('--lb-tau', type=float, default=treeutils.default_lb_tau)
parser.add_argument('--lbr-tau-factor', type=float, default=treeutils.default_lbr_tau_factor)
parser.add_argument('--dont-normalize-lbi', action='store_true')
parser.add_argument('--action', choices=['train', 'test'])
parser.add_argument('--dtr-path')
parser.add_argument('--metric-method', default='dtr')
parser.add_argument('--dtr-cfg')
parser.add_argument('--only-csv-plots', action='store_true')
parser.add_argument('--n-max-queries', type=int)
parser.add_argument('--max-family-size', type=int, help='subset each family down to this size before passing to treeutils')
parser.add_argument('--cluster-indices')
parser.add_argument('--min-selection-metric-cluster-size', type=int, default=treeutils.default_min_selection_metric_cluster_size)
parser.add_argument('--include-relative-affy-plots', action='store_true')
parser.add_argument('--make-tree-plots', action='store_true')
parser.add_argument('--only-look-upwards', action='store_true')
args = parser.parse_args()
args.cluster_indices = utils.get_arg_list(args.cluster_indices, intify_with_ranges=True)
ete_path, workdir = None, None
if args.make_tree_plots:
    ete_path = '/home/%s/anaconda_ete/bin' % os.getenv('USER')
    workdir = utils.choose_random_subdir('/tmp/%s/tree-metrics' % os.getenv('USER'))

if args.n_max_queries is not None:
    print '    --n-max-queries set to %d' % args.n_max_queries
glfo, true_lines, _ = utils.read_output(args.infname, n_max_queries=args.n_max_queries)

# numpy.random.seed(1)
if args.max_family_size is not None:
    for line in [l for l in true_lines if len(l['unique_ids']) > args.max_family_size]:
        iseqs_to_keep = numpy.random.choice(range(len(line['unique_ids'])), args.max_family_size)
        utils.restrict_to_iseqs(line, iseqs_to_keep, glfo)

if args.metric_method == 'dtr':
    raise Exception('I think the [new] first arg here (metrics_to_calc) isn\'t right, but don\'t want to test cause i don\'t care about dtr')
    treeutils.calculate_tree_metrics(['lbi', 'lbr', 'dtr'], None, args.lb_tau, lbr_tau_factor=args.lbr_tau_factor, base_plotdir=args.base_plotdir, only_csv=args.only_csv_plots, min_cluster_size=args.min_selection_metric_cluster_size,
                                     dtr_path=args.dtr_path, train_dtr=args.action=='train', dtr_cfg=args.dtr_cfg, true_lines_to_use=true_lines, include_relative_affy_plots=args.include_relative_affy_plots,
                                     dont_normalize_lbi=args.dont_normalize_lbi, ete_path=ete_path, workdir=workdir, cluster_indices=args.cluster_indices)
else:
    treeutils.calculate_individual_tree_metrics(args.metric_method, true_lines, base_plotdir=args.base_plotdir, lb_tau=args.lb_tau, lbr_tau_factor=args.lbr_tau_factor, only_csv=args.only_csv_plots,
                                                min_cluster_size=args.min_selection_metric_cluster_size, include_relative_affy_plots=args.include_relative_affy_plots,
                                                dont_normalize_lbi=args.dont_normalize_lbi, ete_path=ete_path, workdir=workdir, cluster_indices=args.cluster_indices, only_look_upwards=args.only_look_upwards) #, debug=True)
