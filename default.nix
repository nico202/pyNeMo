with import <nixpkgs> {};
    with pkgs.python27Packages;
    
    buildPythonPackage { 
      name = "pyNeMo";
      buildInputs = [
         git
         python27Packages.pandas
         python27Packages.virtualenv
         python27Packages.pylint
         python27Packages.pillow
         python27Packages.numpy
         python27Packages.pip #Not required, just for testing
         python27Packages.matplotlib
         python27Packages.dill
         python27Packages.web #Required for multiple-machine system
         python27Packages.requests #Required for multiple-machine system
         python27Packages.bpython
         python27Packages.tkinter
         python27Packages.pyflakes
         python27Full
	 yarp
         #Enable image show
         imagemagick
         ( pkgs.callPackage ./yarp-python { })
         ];
      src = null;
    }

