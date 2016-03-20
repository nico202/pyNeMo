#Default number of steps to run. Replace with --steps
STEPS = 1000

#History directory: where to save output by default
#Both absolute or relative path
#Replace with --history
HISTORY_DIR = "./history"

#Try to use the CUDA? Fallback to CPU if fails
#Force one or the other with --cpu/--cuda
#CUDA_BACKEND is the cuda processor to be used
TRY_CUDA = False
CUDA_BACKEND = 0

#Batch config:
#Asks you if you are sure you want to show image on every run?
BATCH_CONFIRM_SHOW_IMAGE = True
#Asks you if you are sure you don't want to save images
BATCH_CONFIRM_NO_SAVE_IMAGE = True
#How frequently we should save batch step
BATCH_SAVE_EVERY = 10

#Deploy system:
MULTIPLIER = 0.5
