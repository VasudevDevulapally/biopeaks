# 1. General Information

`biopeaks` is a graphical user interface for biosignals recorded with the 
Bitalino (link) and OpenSignals (link). The interface is meant for processing
biosignals with rhythmically occuring peaks that
determine the dynamics of the biosignal. A good example is heart rate
derived from the R-peaks in an electrocardiogram (ECG) (link).
`biopeaks` identifies peaks (or more correctly: extrema) in ECG as well as
breathing signals. Based on these peaks you can then calculate statistics, such
as the biosignal's instantaneous period, -rate and in the case of breathing,
-tidal amplitude.
The exact identification of the relevant peaks is a fundamental first step for 
subsequent analyses, such heart rate variability. Errors during peak
identification can  significantly
distort subsequent analyses. Therefore, the intention of `biopeaks`
is to make peak identification convenient and precise. Especially the 
visualization
of the biosignals along with the peaks is crucial in determining if the 
biosignal's quality is sufficient for further analysis. The ability to manually
edit the peaks is equally important, since no algorithm can perfectly identify
all peaks, especially if the biosignal's quality is poor.


# 2. User Guide

## Installation

Go to https://www.anaconda.com/distribution/ and install the lastest 
distribution
for your operating system. Follow the installation instructions in case you're 
unsure
about something: https://docs.anaconda.com/anaconda/install/. Note that
currently, `biopeaks` has only been tested on Windows. In
principle, it should work with Linux and macOS as well.

## Layout of the interface

(link screenshot blank interface)

In the **menubar**, you can find three sections: **_biosignal_**, **_peaks_**,
and **_statistics_**.
These contain methods for the interaction with your biosignals. On the left 
side, there's
an **optionspanel** that allows you to costumize your workflow.
To the right of the **optionspanel** is the **datadisplay** which consists of 
three
panels. The upper
panel contains your biosignal as well as peaks identified in the biosignal, 
while the
middle panel can be used
to optionally display a marker channel. The lower panel contains any statistics 
derived from the peaks. Adjust the height of the panels by dragging the 
segmenters
between them up or down. Beneath the **optionspanel**, in the lower left
corner, you find the **displaytools**. These allow you to interact with your
biosignal. Have a
look in the functionality section (link) for details on any of these elements.

## Functionality
### load biosignal
Before loading the biosignal, you need to select the desired options in
**optionspanel** -> **_channels_**. First, select your _modality_ (ECG for
electrocardiogram, and RESP for breathing). Next, you need to specify which
_biosignal channel_ contains the biosignal corresponding to your modality. You
can let the _biosignal channel_ be inferred from the _modality_, or select a
specific analog channel (A1 through A6). The first option only works if the
biosignal has been declared as belonging to a specific modality in the
OpenSignals recording software. For example an ECG channel must have been
specified as "ECG" before the recording was started in OpenSignals. Optionally, in addition to the _biosignal channel_,
you can select a _marker channel_. This is useful if you recorded a channel
that marks interesting events such as the onset of an experimental condition,
button presses etc.. You can use the _marker channel_ to display any other
channel alongside your _biosignal channel_. Once these options are selected,
you can load the biosignal: **menubar** -> **_biosignal_** -> _load_. A
dialog will let you select the file containing your biosignal. If the biosignal
has been loaded successfully it is displayed in the upper **datadisplay**. If
you selected a _marker channel_, the markers will be displayed in the middle
**datadisplay**.

(link screenshot loaded biosignal & markers)

### segment biosignal
**menubar** -> **_biosignal_** -> _select segment_ opens the **segmentdialog**
on the right side of the **datadisplay**.

(link screenshot segmentdialog)

Specify start and end of the segment in seconds either by entering values in
the respective fields, or with the mouse. For the latter option, first click on
the mouse icon in the respective field and then left-click anywhere on the
upper **datadisplay** to select a time point. To see which time point is
currently under the mouse cursor have a look at the x-coordinate
displayed in the lower right corner of the interface when you hover the mouse
over the upper **datadisplay**.
If you click **_preview segment_**
the segment will be displayed as a shaded region in the upper **datadisplay**
but the segment won't be cut out yet. 

(link screenshot previewed segment)

You can change the start and end values
and preview the segment until you are certain that the desired segment is
selected. Then you can cut out the segment with **_confirm
segment_**. This also closes the **segmentdialog**. Alternatively, the
**segmentdialog** can be closed any time by clicking **_abort segmentation_**.
Clicking **_abort segmentation_** discards any values that might have been
selected. You can segment the biosignal at any time. Other data (peaks,
statistics) will be also be segmented if they are already computed.

### save biosignal
**menubar** -> **_biosignal_** -> _save_ opens a file dialog that lets you
select a directory and file name for saving the biosignal.
Saving the biosignal can be useful after segmentation. Note that the file is
saved in the original OpenSignals format containing all channels.

### find peaks
**menubar** -> **_peaks_** -> _find_ automatically identifies the peaks in the
biosignal. The peaks appear as dots displayed on top of the biosignal.

(link screenshot peaks)

### save peaks
**menubar** -> **_peaks_** -> _save_ opens a file dialog that lets you select a
directory and file name for saving the peaks in a CSV file. The format of the
file depends on the _modality_. For ECG, `biopeaks` saves a column containing
the occurences of R-peaks in seconds. The first element contains the header
"peaks". For breathing, `biopeaks` saves two columns containing the occurences
of inhalation peaks and exhalation troughs respectively in seconds. The first
row contains the header "peaks, troughs". Note that if there are less peaks
than troughs or vice versa, the column with less elements will be padded with
a NaN.

### load peaks
**menubar** -> **_peaks_** -> _load_ opens a file dialog that lets you select
the file containing the peaks. Note that prior to loading the peaks, you have
to load the associated biosignal. Also, loading peaks won't work if there are
already peaks in memory (i.e., if there are already peaks displayed in the
upper **datadisplay**). The peaks appear as dots displayed on top of the
biosignal.

### calculate statistics
**menubar** -> **_statistics_** -> _calculate_ automatically calculates all
possible statistics for the selected _modality_. The statistics will be 
displayed in the lowest **datadisplay**.

(link screenshot statictics)

### save statistics
First select the statistics that you'd like to save: **optionspanel** ->
**_select statictics for saving_**. Then save the selected
statistics: **menubar** -> **_statistics_** -> _save_. This opens a file dialog
that lets you choose a directory and file name for saving a CSV file. The
format of the file depends on the _modality_. Irrespective
of the modality the first two columns contain period and rate.
For breathing, there will be an additional third column containing the tidal
amplitude. The first row contains the header. Note that the statistics are
interpolated to match the biosignal's timescale (i.e., they represent
instantaneous statistics sampled at the biosignal's sampling rate).

### edit peaks
It happens that the automatic peak detection places peaks wrongly. You can
catch these errors by visually inspecting the peak placement. If you spot
errors in peak placement you can correct those manually. To do so make sure to
select **optionspanel** -> **peak options** -> _edit peaks_. Now click on the
upper **datadisplay** once to enable peak editing. To delete a peak place the 
mouse cursor on top of it (or in it's vicinity) and press "d". To add a peak,
press "a". Editing peaks is most convenient if you zoom in on the biosignal
region that you want to edit using the **displaytools** (link). The statistics
can be a useful guide when editing peaks. Isolated, unusually large or small
values in period or rate can indicate misplaced peaks. If the _modality_ is
ECG, peaks are edited automatically during the calculation of the statistics
(link). However, this does not guarantee that all errors in peak placement will
be caught. Always check for error manually! Note, that when editing breathing
extrema, any edits that break the alternation of peaks and troughs
(e.g., two consecutive peaks) will automatically be discarded when you save
the extrema.

### batch processing
**WARNING:** There is no substitute for manually checking your biosignal's
quality as well as the placement of the peaks. Manually checking and editing
peak placement is the only way to guarantee sensible statistics. Only use
batch processing if you are sure that your biosignal's quality is sufficient!

To enable batch processing, select 
**optionspanel** -> **_processing mode_** -> _multiple files_. Make sure to
select the correct _modality_ and _biosignal channel_ in
**optionspanel** -> **_channels_**. Further, indicate if you'd like to save
the peaks during batch processing: **optionspanel** -> **_peak options_** ->
_save peaks during batch processing_. Also, select the statistics you'd like
to save: **optionspanel** -> **_select statictics for saving_**. Now, select
all files that should be included in the batch: **menubar** -> **_biosignal_**
-> _load_. A dialog will let you select the files (select multiple files with
the appropriate keyboard commands of your operating system). Next, a dialog
will ask you to choose a directory for saving the peaks (if you enabled that
option). The peaks will be saved to a file with the same name as the biosignal
file, with a "_peaks" extension.
Finally, a dialog will ask you to select a directory for saving the statistics
(if you chose any statistics for saving). The statistics will be saved to a
file
with the same name as the biosignal file, with a "_stats" extension. Once all
dialogs are closed, `biopeaks` loops over all files in the batch and performs
the following actions for each of them: loading the biosignal, identifying the
peaks, calculating the statistics and finally saving the desired data (peaks
and/or statistics). Note that nothing will be shown in the **datadisplay**
while the batch is processed. You can keep track of the progress by looking
at the file name that is displayed in the lower right corner of the interface.
Note that segmentation or peak editing are not possible during batch
processing.

### displaytools
The **displaytools** allow you to interact with the biosignal. Have a look
[here](https://matplotlib.org/3.1.1/users/navigation_toolbar.html) for a
detailled description of how to use them.


## Getting started
The following workflow is meant as an introduction to the interface. Many other
workflows are possible and might make more sense given your 
requirements. Note that `biopeaks` works with the OpenSignals text file format.
However, you can analyze any data as long as you format your data according to
the OpenSignals convention (link). The functions used in the workflows are
described in detail in the functionality section(link).

### examplary workflow on single file
Time to look at some biosignals! Before you start any workflow, set the desired
options in the **optionspanel**. Make sure that the **_processing mode_** is
set to _single file_ and load your biosignal (link) to visually
check its quality using the **displaytools** (link). Next, if you want, you can
segment  your biosignal (link) based on a specific time interval or events in
the markers. Now, you can identify the peaks in the biosignal (link). If the
quality of the biosignal is sufficient, the peaks should be placed in the
correct locations. However, if there are noisy intervals in the biosignal,
peaks might be misplaced.

(link schreenshot misplaced peak)

If this is the case you can manually edit the
peak locations (link). Once you are confident that all the peaks are placed
correctly you can calculate statistics (link). Finally, you can save any data
that you'd like to keep (links). If you have segmented the biosignal it is a
good idea to save it so you can reproduce the workflow later if necessary. Also
, save the peaks if you're planning on reloading them later (link) or using
them for your own computations.


# 3. Contributor Guide
Please report any bug by opening an issue (link on how to do this). 
Pull requests for new features, improvements, and bug fixes are very welcome!

The application is structured according to a variant of the
[model-view-controller architecture](https://martinfowler.com/eaaDev/uiArchs.html)
To understand the relationship of the model, view, and controller have a look
at how each of them is instantiated in `biopeaks.py`. For
example, the view class has references to the model class as well as the
controller class, whereas the model has no reference to any of the other
components of the architecture (i.e., the model is agnostic to the view and
controller).

# 4. Tests
The test data have been recorded with
software: opensignals v2.0.0, 20190805\
hardware: bitalino revolution (firmware 1281)

# 5. Requirements
+ wfdb
+ Anaconda >= 2019.10

# 6. Further Resources
List links to other OSS packages for further analyses based on statistics
HRV: pyHRV
HR, HRV: biosppy