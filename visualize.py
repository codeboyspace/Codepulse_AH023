import argparse
import os
import yaml
import subprocess
import webbrowser
from auxiliary.laserscan import LaserScan, SemLaserScan
from auxiliary.laserscanvis import LaserScanVis
import subprocess

# Path to the collition.py script
# Execute the command
if __name__ == '__main__':
    # Step 1: Run the collition.py script
    script_path = r'"C:\Users\prane\OneDrive\Desktop\SRM Hackathon\try2\sematic_render_object\semantic_reflect_objects_model\semantic-kitti-api\dataset\sequences\04\collition.py"'

# Command to open a new command prompt window and run the script
    command = f"start cmd /k python {script_path}"
    subprocess.run(command, shell=True)

    # Step 3: Run the main code of visualize.py
    parser = argparse.ArgumentParser("./visualize.py")
    parser.add_argument(
        '--dataset', '-d',
        type=str,
        required=True,
        help='Dataset to visualize. No Default',
    )
    parser.add_argument(
        '--config', '-c',
        type=str,
        required=False,
        default="config/semantic-kitti.yaml",
        help='Dataset config file. Defaults to %(default)s',
    )
    parser.add_argument(
        '--sequence', '-s',
        type=str,
        default="04",
        required=False,
        help='Sequence to visualize. Defaults to %(default)s',
    )
    parser.add_argument(
        '--predictions', '-p',
        type=str,
        default=None,
        required=False,
        help='Alternate location for labels, to use predictions folder. '
        'Must point to directory containing the predictions in the proper format '
        ' (see readme)'
        'Defaults to %(default)s',
    )
    parser.add_argument(
        '--ignore_semantics', '-i',
        dest='ignore_semantics',
        default=False,
        action='store_true',
        help='Ignore semantics. Visualizes uncolored pointclouds.'
        'Defaults to %(default)s',
    )
    parser.add_argument(
        '--do_instances', '-o',
        dest='do_instances',
        default=False,
        required=False,
        action='store_true',
        help='Visualize instances too. Defaults to %(default)s',
    )
    parser.add_argument(
        '--ignore_images', '-r',
        dest='ignore_images',
        default=False,
        required=False,
        action='store_true',
        help='Visualize range image projections too. Defaults to %(default)s',
    )
    parser.add_argument(
        '--link', '-l',
        dest='link',
        default=False,
        required=False,
        action='store_true',
        help='Link viewpoint changes across windows. Defaults to %(default)s',
    )
    parser.add_argument(
        '--offset',
        type=int,
        default=0,
        required=False,
        help='Sequence to start. Defaults to %(default)s',
    )
    parser.add_argument(
        '--ignore_safety',
        dest='ignore_safety',
        default=False,
        required=False,
        action='store_true',
        help='Normally you want the number of labels and ptcls to be the same,'
        ', but if you are not done inferring this is not the case, so this disables'
        ' that safety.'
        'Defaults to %(default)s',
    )
    parser.add_argument(
        '--color_learning_map',
        dest='color_learning_map',
        default=False,
        required=False,
        action='store_true',
        help='Apply learning map to color map: visualize only classes that were trained on',
    )
    FLAGS, unparsed = parser.parse_known_args()

    # print summary of what we will do
    print("*" * 80)
    print("INTERFACE:")
    print("Dataset", FLAGS.dataset)
    print("Config", FLAGS.config)
    print("Sequence", FLAGS.sequence)
    print("Predictions", FLAGS.predictions)
    print("ignore_semantics", FLAGS.ignore_semantics)
    print("do_instances", FLAGS.do_instances)
    print("ignore_images", FLAGS.ignore_images)
    print("link", FLAGS.link)
    print("ignore_safety", FLAGS.ignore_safety)
    print("color_learning_map", FLAGS.color_learning_map)
    print("offset", FLAGS.offset)
    print("*" * 80)

    # open config file
    try:
        print("Opening config file %s" % FLAGS.config)
        CFG = yaml.safe_load(open(FLAGS.config, 'r'))
    except Exception as e:
        print(e)
        print("Error opening yaml file.")
        quit()

    # fix sequence name
    FLAGS.sequence = '{0:02d}'.format(int(FLAGS.sequence))

    # does sequence folder exist?
    scan_paths = os.path.join(FLAGS.dataset, "sequences",
                              FLAGS.sequence, "velodyne")
    if os.path.isdir(scan_paths):
        print(f"Sequence folder {scan_paths} exists! Using sequence from {scan_paths}")
    else:
        print(f"Sequence folder {scan_paths} doesn't exist! Exiting...")
        quit()

    # populate the pointclouds
    scan_names = [os.path.join(dp, f) for dp, dn, fn in os.walk(
        os.path.expanduser(scan_paths)) for f in fn]
    scan_names.sort()

    # does sequence folder exist?
    if not FLAGS.ignore_semantics:
        if FLAGS.predictions is not None:
            label_paths = os.path.join(FLAGS.predictions, "sequences",
                                       FLAGS.sequence, "predictions")
        else:
            label_paths = os.path.join(FLAGS.dataset, "sequences",
                                       FLAGS.sequence, "labels")
        if os.path.isdir(label_paths):
            print(f"Labels folder {label_paths} exists! Using labels from {label_paths}")
        else:
            print(f"Labels folder {label_paths} doesn't exist! Exiting...")
            quit()

        # populate the pointclouds
        label_names = [os.path.join(dp, f) for dp, dn, fn in os.walk(
            os.path.expanduser(label_paths)) for f in fn]
        label_names.sort()

        # check that there are same amount of labels and scans
        if not FLAGS.ignore_safety:
            assert(len(label_names) == len(scan_names))

    # create a scan
    if FLAGS.ignore_semantics:
        scan = LaserScan(project=True)  # project all opened scans to spheric proj
    else:
        color_dict = CFG["color_map"]
        if FLAGS.color_learning_map:
            learning_map_inv = CFG["learning_map_inv"]
            learning_map = CFG["learning_map"]
            color_dict = {key:color_dict[learning_map_inv[learning_map[key]]] for key, value in color_dict.items()}

        scan = SemLaserScan(color_dict, project=True)

    # create a visualizer
    semantics = not FLAGS.ignore_semantics
    instances = FLAGS.do_instances
    images = not FLAGS.ignore_images
    if not semantics:
        label_names = None
    vis = LaserScanVis(scan=scan,
                       scan_names=scan_names,
                       label_names=label_names,
                       offset=FLAGS.offset,
                       semantics=semantics, instances=instances and semantics, images=images, link=FLAGS.link)

    # print instructions
    print("To navigate:")
    print("\tb: back (previous scan)")
    print("\tn: next (next scan)")
    print("\tq: quit (exit program)")

    # run the visualizer
    vis.run()
