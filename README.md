# Galaxy J2 Prime vendor snapshot — LineageOS 18.1

The `lineage-18.1` baseline omitted `lib/hw/camera.mt6735.so` despite retaining
the supporting camera libraries and advertising camera hardware. Restore that
42,800-byte module from this same device repository's pinned `lineage-15.1`
revision. Its Git blob hash matches the module installed on the SM-G532G used
for the 2026-10-25 audit.

See `camera-blob-provenance.json` for the source revision, Git object hash,
SHA-256, size, and direct ELF dependencies. No blob from a different device was
introduced by the camera restoration, and no device calibration was replaced.
The existing recursive `PRODUCT_COPY_FILES` rule installs the restored file.

Static validation confirms an ARM ELF32 library with an `HMI` module export.
This restores a missing prerequisite; camera preview/capture is **not yet
verified**. Pair it with the device branch's camera provider service addition
and validate the legacy camera/framework ABI on Android 11. The connected ROM
reports zero cameras and lacks the provider service binary.

From the project/Android root, using the matching device tree:

```sh
python device/samsung/grandppltedx/tools/audit_vendor.py \
  vendor/samsung/grandppltedx/proprietary/vendor
```

An external ELF dependency in that report is not automatically missing: many
libraries are built by Android. Conversely, ELF inventory does not prove symbol
or namespace compatibility. Bluetooth, GNSS, audio, USB audio and DRM still
require the tests documented in the device tree's `docs/HARDWARE_BRINGUP.md`.

## Android 11 source-built library selection

The recursive blob installation excludes `lib/libalsautils.so`. Android 11's
`audio.usb.default` requires `profile_get_highest_sample_rate`, which the
bundled old library does not export. That copy previously overwrote the
source-built module, matching the linker error observed on the phone. The
MTK primary audio HAL lists this dependency but imports none of its symbols.
The original blob remains in the repository for provenance. USB playback and
capture still require device testing after building the coherent image.

The `libion_mtk` Soong module now references `libion_mtk.so`; it previously
referenced `libdpframework.so`. Only the correct blob exports
`ion_custom_ioctl`, which the device's graphics code calls. Both graphics
prebuilts are packaged through their modules, excluding duplicate raw copies.

The old `lib/libshim_gui.so` is also excluded from raw copying. It overwrote the
device's source-built shim and lacks the old unsigned mapper-lock implementation
needed by `hwcomposer.mt6735.so`. The first VM ROM consequently stayed at the
Samsung logo while Android repeatedly waited for its display service. Pair this
exclusion with the device's updated GUI shim/CallStack dependency. Before/after
`dlopen(RTLD_NOW)` tests reproduce the original composer/camera errors and load
both with the new shim; normal boot and hardware operation remain to be tested.

## Audio-filter calibration IDs

`libaudiocompensationfilter_vendor.so` used NVRAM LIDs two entries higher than
the bundled `libcustom_nvram.so` table. Its default getter/setter selected LID
53 (`WIFI`, 512 bytes) instead of 51 (`Audio_CompFlt`, 1260 bytes). The installed
phone logs the corresponding failed Wi-Fi-record access during audio-filter
initialization and falls back to default filter parameters. The filter's six
table selections have the same +2 bias.

Eight constant bytes are corrected: the getter/setter defaults and the shared
six-entry selection table. All seven filter types now resolve to the intended
audio files with 1260-byte records. No file access permissions, calibration
contents, record format, or DSP coefficients are changed. This corrects record
selection; playback quality and persistence still require physical testing.

`audio-filter-lid-provenance.json` records the original Git object, source
revision, input/output SHA-256, exact byte preconditions and offsets. Reproduce
or verify the patch with `python3 tools/fix_audio_filter_lids.py --apply` or
`python3 tools/fix_audio_filter_lids.py`. The tool rejects unknown binaries.
From the Android root, independently check both library/table contents with:

```sh
python3 device/samsung/grandppltedx/tools/validate_audio_nvram.py \
  vendor/samsung/grandppltedx/proprietary/vendor
```

The checker rejects the original library because it selects the Wi-Fi record.
The corrected library passes all seven file/type/size checks. Raw NVRAM data
was never read or modified by this source correction.
