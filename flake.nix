{
  description = "Linux Desktop Gremlins brings animated mascots to your Linux desktop";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs =
    { self, nixpkgs }:
    let
      supportedSystems = [
        "x86_64-linux"
        "aarch64-linux"
      ];

      forAllSystems =
        f:
        builtins.listToAttrs (
          map (system: {
            name = system;
            value = f system;
          }) supportedSystems
        );

    in
    {
      packages = forAllSystems (
        system:
        let
          pkgs = import nixpkgs { inherit system; };
        in
        {
          linux-desktop-gremlin = pkgs.callPackage ./default.nix { };
          default = self.packages.${system}.linux-desktop-gremlin;
        }
      );
    };
}
