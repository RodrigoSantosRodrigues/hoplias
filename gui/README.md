## Downloads

[![Windows](https://img.shields.io/badge/Windows-Download-blue?style=for-the-badge&logo=windows)](./dist_win/Hoplias%20gui%20Setup%201.0.0-alpha.exe)
[![macOS](https://img.shields.io/badge/macOS-Download-silver?style=for-the-badge&logo=apple)](./dist_mac/Hoplias%20gui-1.0.0-alpha-mac.zip)
[![Linux](https://img.shields.io/badge/Linux-Download-orange?style=for-the-badge&logo=linux)](./dist_linux/hoplias-gui_1.0.0-alpha_amd64.AppImage)


### Specific versions
| Plataforma     | Arquivo    | Download                                                                                    |
|----------------|------------|---------------------------------------------------------------------------------------------|
| Windows .exe   | Installer  | [Hoplias gui Setup 1.0.0-alpha.exe](./dist_win/Hoplias%20gui%20Setup%201.0.0-alpha.exe)   |
| macOS  .zip    | Zip        | [Hoplias gui-1.0.0-alpha-mac.zip](./dist_mac/Hoplias%20gui-1.0.0-alpha-mac.zip)               |
| Linux .deb     | AppImage   | [hoplias-gui_1.0.0-alpha_amd64.de](./dist_linux/hoplias-gui_1.0.0-alpha_amd64.deb)          |
| Linux  .tar    | AppImage   | [hoplias-gui-1.0.0-alpha.tar.xz](./dist_linux/hoplias-gui-1.0.0-alpha.tar.xz)               |



## Development mode
- Install `yarn`
- Starting server `yarn start`

## Notes
- Node >=20
- Required 

## 🚀 Deploys
## Option 1: Building default
- Required node >=20.
- comand `yarn build:win`.
- rename folder `dist` to `dist_win`

- comand `yarn build:linux`.
- rename folder `dist` to `dist_linux`

- comand `yarn build:mac`.
- rename folder `dist` to `dist_mac`

## Option 2: Buildinf with docker
- Required docker instaled.

## 🐧 Building Linux
### PowerShell
`docker build -t hoplias-gui-builder .`
`docker run --rm -v "${PWD}/dist:/output" hoplias-gui-builder`

### CMD (Command Prompt)
`docker build -t hoplias-gui-builder .`
`docker run --rm -v "%cd%\dist:/output" hoplias-gui-builder`


## 🍏 Building Mac
### PowerShell
`docker build -t hoplias-gui-builder --build-arg BUILD_TARGET=mac .`
`docker build -t hoplias-gui-builder .`

### CMD (Command Prompt)
`docker build -t hoplias-gui-builder --build-arg BUILD_TARGET=mac .`
`docker run --rm -v "%cd%\dist:/output" hoplias-gui-builder`


## 🖥️ Building Windows
### PowerShell
`docker build -t hoplias-gui-builder --build-arg BUILD_TARGET=mac .`
`docker build -t hoplias-gui-builder .`

### CMD (Command Prompt)
`docker build -t hoplias-gui-builder --build-arg BUILD_TARGET=win .`
`docker run --rm -v "%cd%\dist:/output" hoplias-gui-builder`
