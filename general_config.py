steps = 10000       #if step == 0, run indefinitely (how to stop?)

#Prevent different Runner version from being considered the same config
commit_version = open(".git/refs/heads/master", 'r').readline().rstrip()

#those starting with "_" are excluded from the hasing
_history_dir = ".store"
_DEBUG = False        #Print some stats
_OUTPUT = False      #print spikes
_GPU = False          #GPU or CPU?
_BACKEND_NUMBER = -1  #Used for GPU only. -1 = Default
_SHOW_IMAGE_ON_SAVE = False #Disable if running batch
_SHOW_SPIKES = False   #Show a file with all the neurons
_SHOW_MEMBRANE = False #Show as many pictures as neurons marked as "save"
_FILE_EXT = ".png"  #Still to add
