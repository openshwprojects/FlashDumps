# Tuya OTA firmware catalogue

Firmware offered by Tuya, organised by the OTA channel reported for the component being updated. A channel does not identify the chipset: for example, channel 9 includes both secondary-MCU firmware and some Linux host-processor packages.

| Channel | Tuya component label | Typical updates | Unique cached files |
|---:|---|---|---:|
| [0](channel-0/) | Main Module | Main network/application firmware, commonly Wi-Fi modules and gateways | 366 |
| [1](channel-1/) | Bluetooth Module | Bluetooth/BLE modules and components | 115 |
| [3](channel-3/) | ZigBee Module | Zigbee modules, coordinators and components | 142 |
| [9](channel-9/) | MCU Module | MCU/application firmware, including some host-processor packages | 502 |

There are **1125 unique cached binaries** across these folders. The channel-9 total includes one separately labelled, MD5-verified camera second-stage download; it was referenced by an updater, not independently offered by the Tuya API.

Each channel README lists the filename, product key, target version, OTA changelog and original download URL. Release notes are retained from Tuya responses where captured. Three older channel-9 entries instead use their matching update screenshots. Historical URL-list entries without a captured response have blank changelog cells and do not acquire guessed product keys or release notes.

Identical bytes are stored once per collection, even when offered for multiple product keys or found at different CDN URLs. Existing researched channel-9 filenames have been preserved. Channel-0 files retain their original Tuya download filenames. Other channels retain descriptive Tuya download names or evidence-supported device identifications; naming is not a guarantee of compatibility with another device.

Files larger than our 100 MiB repository cutoff are kept locally and listed without a repository-file link. This applies to the Eufy RoboVac S1 Pro package in channel 9, the Nova Digital MidPanel 8 package in channel 0, and the XZ-AZK101 control-screen package in channel 0. The remaining 1122 cached binaries have repository-file links.

One additional historical channel-0 entry, `1626070894-oem_bk7231s_light_ug_3.0.1.bin`, could not be downloaded: its public locations return HTTP 403. It remains listed without a local-file link.

Matching update screenshots are retained in [channel-9/images/](channel-9/images/). The previous [TuyaMCUBins OTA location](../../TuyaMCUBins/OTA/) now points here; full MCU backups remain separate from this OTA collection.
