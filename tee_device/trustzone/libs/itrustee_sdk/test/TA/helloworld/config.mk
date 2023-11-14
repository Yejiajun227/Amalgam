#
# Copyright (c) Huawei Technologies Co., Ltd. 2022-2022. All rights reserved.
#
# API_LEVEL which indicates the GP API version of TA
# API_LEVEL=1 indicates GP 1.0 which is the current version of itrustee
# API_LEVEL=2 indicates GP 1.1.1 which is the current version of the partner
# API_LEVEL=3 indicates GP 1.2 which is the version we both going to support
# If no API_LEVEL is specified, API of GP 1.0 will be taken
#
# USE_SMEE which indicates the feature of sram memory encryption
# USE_SMEE=y indicates the feature of sram memory encryption will be enabled
# If no USE_SMEE is specified, smee feature will not be disabled
# If USE_SMEE is specified and a section is custimized,
# explicitly specify the segment to which the section belongs in the link script(ta_link_64.smee.ld)

CFLAGS += -DAPI_LEVEL=1
USE_SMEE = n
ifeq ($(TARGET_IS_ARM64),)
    TARGET_IS_ARM64 = y
endif
ifeq ($(USE_SMEE),)
    USE_SMEE = n
endif
