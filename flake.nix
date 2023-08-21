{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/23.05";
    nixpkgs_top500.url = "github:nixos/nixpkgs/dce8fc727dc2891628e4f878bb18af643b7b255d";
  };

  outputs = { self, nixpkgs, nixpkgs_top500 }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
      pkgs_top500 = import nixpkgs_top500 { inherit system; };
    in
    {
      devShells.${system} = {
        default = pkgs.mkShell {
          buildInputs = [
            pkgs_top500.python3
            pkgs_top500.python3Packages.xlrd
            pkgs_top500.python3Packages.matplotlib
            pkgs_top500.python3Packages.pandas
            pkgs_top500.python3Packages.mechanize
          ];
        };
      };
    };
}
