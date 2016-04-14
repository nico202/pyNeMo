{ stdenv, fetchFromGitHub, ace, cmake, python, ruby, swig, yarp
}:

stdenv.mkDerivation rec {
  name = "yarp-bindings-${version}";
  version = yarp.version;

  src = yarp.src;

  preConfigure = "cd bindings";

  cmakeFlags = [
    "-DCREATE_PYTHON=TRUE"
    "-DCREATE_RUBY=TRUE"
  ];

  buildInputs = [ cmake ace ruby swig yarp python ];

  enableParallelBuilding = true;

  meta = yarp.meta;
}

