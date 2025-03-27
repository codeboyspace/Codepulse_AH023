# LidAR Spoofing Attack prevention

This repository contains the data for backend and also frontend for Spoofing attack preventive measure and accuracy enhancement of sensor to improve much better decision making by the Decision Controller.
---
##### Example of 3D pointcloud from sequence:
<img src="https://image.ibb.co/kyhCrV/scan1.png" width="1000">
---

#### Frontend Link for Visulization: https://lidar-spoofi.vercel.app/
## Data organization

The data is organized in the following format:

```
/kitti/dataset/
          └── sequences/
                  ├── 00/
                  │   ├── poses.txt
                  │   ├── image_2/
                  │   ├── image_3/
                  │   ├── labels/
                  │   │     ├ 000000.label
                  │   │     └ 000001.label
                  |   ├── voxels/
                  |   |     ├ 000000.bin
                  |   |     ├ 000000.label
                  |   |     ├ 000000.occluded
                  |   |     ├ 000000.invalid
                  |   |     ├ 000001.bin
                  |   |     ├ 000001.label
                  |   |     ├ 000001.occluded
                  |   |     ├ 000001.invalid
                  │   └── velodyne/
                  │         ├ 000000.bin
                  │         └ 000001.bin
                  ├── 01/
                  ├── 02/
                  .
                  .
                  .
                  └── 21/
```

- From [KITTI Odometry](http://www.cvlibs.net/datasets/kitti/eval_odometry.php): 
  - `image_2` and `image_3` correspond to the rgb images for each sequence.
  - `velodyne` contains the pointclouds for each scan in each sequence. Each 
`.bin` scan is a list of float32 points in [x,y,z,remission] format. See
[laserscan.py](auxiliary/laserscan.py) to see how the points are read.
- From SemanticKITTI:
  - `labels` contains the labels for each scan in each sequence. Each `.label` 
file contains a uint32 label for each point in the corresponding `.bin` scan.
See [laserscan.py](auxiliary/laserscan.py) to see how the labels are read.
  - `poses.txt` contain the manually looped-closed poses for each capture (in
the camera frame) that were used in the annotation tools to aggregate all
the point clouds.
  - `voxels` contains all information needed for the task of semantic scene completion. Each `.bin` file contains for each voxel if that voxel is occupied by laser measurements in a packed binary format. This is the input to the semantic scene completion task and it corresponds to the voxelization of a single LiDAR scan. Each`.label` file contains for each voxel of the completed scene a label in binary format. The label is a 16-bit unsigned integer (aka uint16_t) for each voxel. `.invalid` and `.occluded` contain information about the occlusion of voxel. Invalid voxels are voxels that are occluded from each view position and occluded voxels are occluded in the first view point. See also [SSCDataset.py](auxiliary/SSCDataset.py) for more information on loading the data.

The main configuration file for the data is in `config/semantic-kitti.yaml`. In this file you will find:

- `labels`: dictionary which maps numeric labels in `.label` file to a string class. Example: `10: "car"`
- `color_map`: dictionary which maps numeric labels in `.label` file to a bgr color for visualization. Example `10: [245, 150, 100] # car, blue-ish`
- `content`: dictionary with content of each class in labels, as a ratio to 
the number of total points in the dataset. This can be obtained by running the
[./content.py](./content.py) script, and is used to calculate the weights for the cross
entropy in all baseline methods (in order handle class imbalance).
- `learning_map`: dictionary which maps each class label to its cross entropy
equivalent, for learning. This is done to mask undesired classes, map different
classes together, and because the cross entropy expects a value in
[0, numclasses - 1]. We also provide [./remap_semantic_labels.py](./remap_semantic_labels.py),
a script that uses this dictionary to put the label files in the cross entropy format,
so that you can use the labels directly in your training pipeline.
Examples:
  ```yaml
    0 : 0     # "unlabeled"
    1 : 0     # "outlier" to "unlabeled" -> gets ignored in training, with unlabeled
    10: 1     # "car"
    252: 1    # "moving-car" to "car" -> gets merged with static car class
  ```
- `learning_map_inv`: dictionary with inverse of the previous mapping, allows to
map back the classes only to the interest ones (for saving point cloud predictions
in original label format). We also provide [./remap_semantic_labels.py](./remap_semantic_labels.py),
a script that uses this dictionary to put the label files in the original format,
when instantiated with the `--inverse` flag.
- `learning_ignore`: dictionary that contains for each cross entropy class if it
will be ignored during training and evaluation or not. For example, class `unlabeled` gets
ignored in both training and evaluation.
- `split`: contains 3 lists, with the sequence numbers for training, validation, and evaluation.


## Dependencies for API:

System dependencies

```sh
$ sudo apt install python3-dev python3-pip python3-pyqt5.qtopengl # for visualization
```

Python dependencies

```sh
$ sudo pip3 install -r requirements.txt
```

## Scripts:

**ALL OF THE SCRIPTS CAN BE INVOKED WITH THE --help (-h) FLAG, FOR EXTRA INFORMATION AND OPTIONS.**

#### Visualization 


##### Point Clouds

To visualize the data, use the `visualize.py` script. It will open an interactive
opengl visualization of the pointclouds along with a spherical projection of
each scan into a 64 x 1024 image.

```sh
$ ./visualize.py --sequence 00 --dataset /path/to/kitti/dataset/
```

where:
- `sequence` is the sequence to be accessed.
- `dataset` is the path to the kitti dataset where the `sequences` directory is.

Navigation:
- `n` is next scan,
- `b` is previous scan,
- `esc` or `q` exits.

In order to visualize your predictions instead, the `--predictions` option replaces
visualization of the labels with the visualization of your predictions:

```sh
$ ./visualize.py --sequence 00 --dataset /path/to/kitti/dataset/ --predictions /path/to/your/predictions
```

To directly compare two sets of data, use the `compare.py` script. It will open an interactive
opengl visualization of the pointcloud labels.

```sh
$ ./compare.py --sequence 00 --dataset_a /path/to/dataset_a/ --dataset_b /path/to/kitti/dataset_b/
```

where:
- `sequence` is the sequence to be accessed.
- `dataset_a` is the path to a dataset in KITTI format where the `sequences` directory is.
- `dataset_b` is the path to another dataset in KITTI format where the `sequences` directory is.

Navigation:
- `n` is next scan,
- `b` is previous scan,
- `esc` or `q` exits.

#### Voxel Grids for Semantic Scene Completion

To visualize the data, use the `visualize_voxels.py` script. It will open an interactive
opengl visualization of the voxel grids and options to visualize the provided voxelizations 
of the LiDAR data.

```sh
$ ./visualize_voxels.py --sequence 00 --dataset /path/to/kitti/dataset/
```

where:
- `sequence` is the sequence to be accessed.
- `dataset` is the path to the kitti dataset where the `sequences` directory is.

Navigation:
- `n` is next scan,
- `b` is previous scan,
- `esc` or `q` exits.

Note: Holding the forward/backward buttons triggers the playback mode.


#### LiDAR-based Moving Object Segmentation ([LiDAR-MOS](https://zithub.com/PRBonn/LiDAR-MOS))

To visualize the data, use the `visualize_mos.py` script. It will open an interactive
opengl visualization of the voxel grids and options to visualize the provided voxelizations 
of the LiDAR data.

```sh
$ ./visualize_mos.py --sequence 00 --dataset /path/to/kitti/dataset/
```

where:
- `sequence` is the sequence to be accessed.
- `dataset` is the path to the kitti dataset where the `sequences` directory is.

Navigation:
- `n` is next scan,
- `b` is previous scan,
- `esc` or `q` exits.

Note: Holding the forward/backward buttons triggers the playback mode.


#### Evaluation
For semantic segmentation, we provide the `remap_semantic_labels.py` script to make this 
shift before the training, and once again before the evaluation, selecting which are the interest 
classes in the configuration file. 
The data needs to be either:

- In a separate directory with this format:

  ```
  /method_predictions/
            └── sequences
                ├── 00
                │   └── predictions
                │         ├ 000000.label
                │         └ 000001.label
                ├── 01
                ├── 02
                .
                .
                .
                └── 21
  ```

  And run:

  ```sh
  $ ./evaluate_semantics.py --dataset /path/to/kitti/dataset/ --predictions /path/to/method_predictions --split train/valid/test # depending of desired split to evaluate
  ```

  or 

    ```sh
  $ ./evaluate_completion.py --dataset /path/to/kitti/dataset/ --predictions /path/to/method_predictions --split train/valid/test # depending of desired split to evaluate
  ```

  or 

    ```sh
  $ ./evaluate_panoptic.py --dataset /path/to/kitti/dataset/ --predictions /path/to/method_predictions --split train/valid/test # depending of desired split to evaluate
  ```

  or for moving object segmentation

    ```sh
  $ ./evaluate_mos.py --dataset /path/to/kitti/dataset/ --predictions /path/to/method_predictions --split train/valid/test # depending of desired split to evaluate
  ```  

- In the same directory as the dataset

  ```
  /kitti/dataset/
            ├── poses
            └── sequences
                ├── 00
                │   ├── image_2
                │   ├── image_3
                │   ├── labels
                │   │     ├ 000000.label
                │   │     └ 000001.label
                │   ├── predictions
                │   │     ├ 000000.label
                │   │     └ 000001.label
                │   └── velodyne
                │         ├ 000000.bin
                │         └ 000001.bin
                ├── 01
                ├── 02
                .
                .
                .
                └── 21

  ```
