{ pkgs, lib, ... }:
let
  clang = pkgs.clang_14;
  run-extensions = [ ".c" ]; # use this list for file-param runners because
  # we don't want .h files to be runnable
  clang-compile = import ../../clang-compile {
    inherit pkgs;
    inherit clang;
  };
  dap-cpp = pkgs.callPackage ../../dap-cpp { };
  dap-cpp-messages = import ../../dap-cpp/messages.nix;

  clang-version = lib.versions.majorMinor clang.version;
in
{
  id = "c-clang${clang-version}";
  name = "C Tools (with Clang)";
  version = "1.0";

  packages = [
    clang
  ];

  replit.runners.clang-project = {
    name = "Clang: Project";
    compile = "${clang-compile}/bin/clang-compile main.c c all";
    fileParam = false;
    language = "c";
    start = "./main.c.bin";
  };

  # TODO: add back single runners/debuggers when we have priority for runners
  # we want to avoid an unstable first runner for users
  # that do not have multiple runners turned on

  # replit.runners.clang-single = {
  #   name = "Clang: Single File";
  #   compile = "${clang-compile}/bin/clang-compile $file c single";
  #   fileParam = true;
  #   language = "c";
  #   extensions = run-extensions;
  #   start = "./\${file}.bin";
  # };

  replit.languageServers.ccls = {
    name = "ccls";
    language = "c";
    start = "${pkgs.ccls}/bin/ccls";
  };

  replit.debuggers.gdb-project = {
    name = "GDB: Project";
    language = "c";
    start = "${dap-cpp}/bin/dap-cpp";
    fileParam = false;
    compile = "${clang-compile}/bin/clang-compile main.c c all debug";
    transport = "stdio";
    initializeMessage = dap-cpp-messages.dapInitializeMessage;
    launchMessage = dap-cpp-messages.dapLaunchMessage "./main.c.bin";
  };

  # replit.debuggers.gdb-single = {
  #   name = "GDB: Single File";
  #   language = "c";
  #   extensions = run-extensions;
  #   start = "${dap-cpp}/bin/dap-cpp";
  #   fileParam = true;
  #   compile = "${clang-compile}/bin/clang-compile $file c single debug";
  #   transport = "stdio";
  #   initializeMessage = dapInitializeMessage;
  #   launchMessage = dapLaunchMessage "./$file.bin";
  # };
}