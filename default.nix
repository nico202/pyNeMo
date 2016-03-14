with import <nixpkgs> {};
    with pkgs.python27Packages;
    
    buildPythonPackage { 
      name = "pyNeMo";
      buildInputs = [
         git
         python27Packages.pandas
         python27Packages.virtualenv
         python27Packages.pillow
         python27Packages.numpy
         python27Full
         ];
      src = null;
    }

