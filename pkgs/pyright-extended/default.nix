{ pkgs, lib, ... }:
let
  version = "2.0.6";
in
pkgs.stdenvNoCC.mkDerivation rec {
  pname = "pyright-extended";
  inherit version;

  src = pkgs.fetchurl {
    url = "https://registry.npmjs.org/@replit/pyright-extended/-/pyright-extended-${version}.tgz";
    hash = "sha256-BtKq3Qb3ujgTkZOJHyLaIbaqgk9yh+fgypPhYL8lM+o=";
  };

  binPath = lib.makeBinPath [
    pkgs.ruff
    pkgs.yapf
    pkgs.nodejs_18
  ];

  nativeBuildInputs = [
    pkgs.makeWrapper
  ];

  dontConfigure = true;
  dontBuild = true;

  installPhase = ''
    runHook preInstall
    mkdir -p $out/lib
    cp -r . $out/lib
    mkdir -p $out/bin
    makeWrapper "$out/lib/index.js" "$out/bin/index.js" \
      --prefix PATH : "${binPath}"
    makeWrapper "$out/lib/langserver.index.js" "$out/bin/langserver.index.js" \
      --prefix PATH : "${binPath}"
    runHook postInstall
  '';
}
