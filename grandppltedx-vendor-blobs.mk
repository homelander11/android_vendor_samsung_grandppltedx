# Keep Android 11's libalsautils paired with its audio.usb.default HAL. The
# bundled older copy lacks profile_get_highest_sample_rate and overwrites the
# source-built library. The MTK primary HAL has no symbol imports from it.
PRODUCT_COPY_FILES += $(filter-out \
    vendor/samsung/grandppltedx/proprietary/vendor/lib/libalsautils.so:%,\
    $(call find-copy-subdir-files,*,vendor/samsung/grandppltedx/proprietary/vendor,$(TARGET_COPY_OUT_VENDOR)))


