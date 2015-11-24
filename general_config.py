steps = 10000       #if step == 0, run indefinitely (how to stop?)

#Prevent different Runner version being considered the same config
commit_version = open(".git/refs/heads/master", 'r').readline().rstrip()

#those starting with "_" are excluded from the hasing
_history_dir = ".store"
_DEBUG = True        #Print some stats
_OUTPUT = False      #print spikes
_GPU = True          #GPU or CPU?
_BACKEND_NUMBER = -1  #Used for GPU only. -1 = Default
