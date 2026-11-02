# Tuya OTA firmware catalogue

Firmware offered by Tuya, organised by the OTA channel reported for the component being updated. A channel does not identify the chipset: for example, channel 9 includes both secondary-MCU firmware and some Linux host-processor packages.

| Channel | Tuya component label | Typical updates | Unique cached files |
|---:|---|---|---:|
| [0](channel-0/) | Main Module | Main network/application firmware, commonly Wi-Fi modules and gateways | 951 |
| [1](channel-1/) | Bluetooth Module | Bluetooth/BLE modules and components | 128 |
| [3](channel-3/) | ZigBee Module | Zigbee modules, coordinators and components | 160 |
| [9](channel-9/) | MCU Module | MCU/application firmware, including some host-processor packages | 534 |
| [10](channel-10/) | Other type | Product-specific component; offerings link to identical bytes stored in channels 0 or 9 | 2 |
| [12](channel-12/) | Other type | Product-specific component; observed AIR32F103-targeted firmware for RF Water Timer | 2 |

There are **1777 unique cached binaries** in the catalogue, including oversized payloads that are not included in the public repository. The channel-9 total includes one separately labelled, MD5-verified camera second-stage download; it was referenced by an updater, not independently offered by the Tuya API.

Each channel README lists the filename, product key, target version, OTA changelog and original download URL. Release notes are retained from Tuya responses where captured. Three older channel-9 entries instead use their matching update screenshots. Historical URL-list entries without a captured response have blank changelog cells and do not acquire guessed product keys or release notes.

Identical bytes are stored once per collection, even when offered for multiple product keys or found at different CDN URLs. When the same bytes are offered on multiple channels, each channel README records its own offering and links to the single stored file. Original Tuya download filenames are used across channels where captured. Three historical channel-9 files retain descriptive names because their originals were not recorded. Device/model and platform/MCU information is retained in each channel README and the private catalogue; naming is not a guarantee of compatibility.

Files larger than our 100 MiB repository cutoff are kept locally and listed without a repository-file link. This applies to the Eufy RoboVac S1 Pro package in channel 9, the Nova Digital MidPanel 8 package in channel 0, the XZ-AZK101 control-screen package in channel 0, and the Dustin 7100 RK3326 package in channel 0. Also retained locally without a repository-file link: Control Panel MAX EU (channel 0, `1781261005e77c5d8b370.bin`). Also retained locally without a repository-file link: 4'' Smart panel-AP (channel 0, `1721198888-un_dgnzk_ld_OTA_3.3.8.bin`). Also retained locally without a repository-file link: eufy S1200 (channel 0, `17576778653e9889248b1.tar.gz`). Also retained locally without a repository-file link: 4'' Smart panel-EU (channel 0, `1720077069-eu_dgnzk_ld_OTA_3.3.9.bin`). The remaining 1769 cached binaries have repository-file links.

One additional historical channel-0 entry, `1626070894-oem_bk7231s_light_ug_3.0.1.bin`, could not be downloaded: its public locations return HTTP 403. It remains listed without a local-file link.

Matching update screenshots are retained in [channel-9/images/](channel-9/images/). The previous [TuyaMCUBins OTA location](../../TuyaMCUBins/OTA/) now points here; full MCU backups remain separate from this OTA collection.
