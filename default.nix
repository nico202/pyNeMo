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
         cmake
	 yarp
         curl #julia-gtk
         llvm
         clang
         glib
         julia
         #Enable image show
         imagemagick
         ( pkgs.callPackage ./yarp-python { })
         ];
      src = null;
      shellHook = ''
       unset http_proxy
      export SSL_CERT_FILE=/etc/ssl/certs/ca-bundle.crt
      export GIT_SSL_CAINFO=/etc/ssl/certs/ca-bundle.crt
      '';
    }

