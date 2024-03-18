{ pkgs ? import <nixpkgs> {} }:
with pkgs;
let
  pyPackages = ps: with ps; [ requests requests_toolbelt requests_oauthlib ];
  py = python311.withPackages pyPackages;
in
  mkShell {
    shellHook = ''
    source shellHook.sh
    exec fish
    '';
    packages = [ py ];
  }
