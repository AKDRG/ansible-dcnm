# -*- coding: utf-8 -*-
# @author: Allen Robel
# @file: plugins/module_utils/vrf/vrf_playbook_model.py
# Copyright (c) 2020-2023 Cisco and/or its affiliates.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# pylint: disable=wrong-import-position
"""
Validation model for dcnm_vrf playbooks.
"""
from typing import Optional, Union

from pydantic import BaseModel, ConfigDict, Field, StrictBool, field_validator

from ..common.enums.bgp import BgpPasswordEncrypt
from ..common.models.ipv4_cidr_host import IPv4CidrHostModel
from ..common.models.ipv4_host import IPv4HostModel
from ..common.models.ipv4_multicast_group_address import IPv4MulticastGroupModel
from ..common.models.ipv6_cidr_host import IPv6CidrHostModel
from ..common.models.ipv6_host import IPv6HostModel


class PlaybookVrfLiteModel(BaseModel):
    """
    # Summary

    Model for VRF Lite configuration.

    ## Raises

    - ValueError if:
      - dot1q is not within the range 0-4094
      - ipv4_addr is not valid
      - ipv6_addr is not valid
      - interface is not provided
      - neighbor_ipv4 is not valid
      - neighbor_ipv6 is not valid

    ## Attributes:

    - dot1q (int): VLAN ID for the interface.
    - interface (str): Interface name.
    - ipv4_addr (str): IPv4 address in CIDR format.
    - ipv6_addr (str): IPv6 address in CIDR format.
    - neighbor_ipv4 (str): IPv4 address without prefix.
    - neighbor_ipv6 (str): IPv6 address without prefix.
    - peer_vrf (str): Peer VRF name.

    ## Example usage:

    ```python
    from pydantic import ValidationError
    from vrf_lite_module import PlaybookVrfLiteModel
    try:
        vrf_lite = PlaybookVrfLiteModel(
            dot1q=100,
            interface="Ethernet1/1",
            ipv4_addr="10.1.1.1/24"
        )
    except ValidationError as e:
        handle_error
    ```

    """

    dot1q: str = Field(default="", max_length=4)
    interface: str
    ipv4_addr: Optional[str] = Field(default="")
    ipv6_addr: Optional[str] = Field(default="")
    neighbor_ipv4: Optional[str] = Field(default="")
    neighbor_ipv6: Optional[str] = Field(default="")
    peer_vrf: Optional[str] = Field(default="", min_length=1, max_length=32)

    @field_validator("dot1q", mode="before")
    @classmethod
    def validate_dot1q_and_serialize_to_str(cls, value: Union[None, int, str]) -> str:
        """
        Validate dot1q and serialize it to a str.

        - If value is any of [None, "", "0", 0], return an empty string.
        - Else, if value cannot be converted to an int, raise ValueError.
        - Convert to int and validate it is within the range 1-4094.
        - If it is, return the value as a string.
        - If it is not, raise ValueError.
        """
        if value in [None, "", "0", 0]:
            return ""
        try:
            value = int(value)
        except (ValueError, TypeError) as error:
            msg = f"Invalid dot1q value: {value}. It must be an integer between 1 and 4094."
            msg += f" Error detail: {error}"
            raise ValueError(msg) from error
        if value < 1 or value > 4094:
            raise ValueError(f"Invalid dot1q value: {value}. It must be an integer between 1 and 4094.")
        return str(value)

    @field_validator("neighbor_ipv4", mode="before")
    @classmethod
    def validate_neighbor_ipv4(cls, value: str) -> str:
        """
        Validate neighbor_ipv4 is an IPv4 host address without prefix.
        """
        if value != "":
            IPv4HostModel(ipv4_host=str(value))
        return value

    @field_validator("neighbor_ipv6", mode="before")
    @classmethod
    def validate_neighbor_ipv6(cls, value: str) -> str:
        """
        Validate neighbor_ipv6 is an IPv6 host address without prefix.
        """
        if value != "":
            IPv6HostModel(ipv6_host=str(value))
        return value

    @field_validator("ipv4_addr", mode="before")
    @classmethod
    def validate_ipv4_addr(cls, value: str) -> str:
        """
        Validate ipv4_addr is a CIDR-format IPv4 host address.
        """
        if value != "":
            IPv4CidrHostModel(ipv4_cidr_host=str(value))
        return value

    @field_validator("ipv6_addr", mode="before")
    @classmethod
    def validate_ipv6_addr(cls, value: str) -> str:
        """
        Validate ipv6_addr is a CIDR-format IPv6 host address.
        """
        if value != "":
            IPv6CidrHostModel(ipv6_cidr_host=str(value))
        return value


class PlaybookVrfAttachModel(BaseModel):
    """
    # Summary

    Model for VRF attachment configuration.

    ## Raises

    - ValueError if:
        - deploy is not a boolean
        - export_evpn_rt is not a string
        - import_evpn_rt is not a string
        - ip_address is not a valid IPv4 host address
        - ip_address is not provided
        - vrf_lite (if provided) is not a list of PlaybookVrfLiteModel instances

    ## Attributes:

    - deploy (bool): Flag to indicate if the VRF should be deployed.
    - export_evpn_rt (str): Route target for EVPN export.
    - import_evpn_rt (str): Route target for EVPN import.
    - ip_address (str): IP address of the interface.
    - vrf_lite (list[PlaybookVrfLiteModel]): List of VRF Lite configurations.
    - vrf_lite (None): If not provided, defaults to None.

    ## Example usage:

    ```python
    from pydantic import ValidationError
    from vrf_attach_module import PlaybookVrfAttachModel
    try:
        vrf_attach = PlaybookVrfAttachModel(
            deploy=True,
            export_evpn_rt="target:1:1",
            import_evpn_rt="target:1:2",
            ip_address="10.1.1.1",
            vrf_lite=[
                PlaybookVrfLiteModel(
                    dot1q=100,
                    interface="Ethernet1/1",
                    ipv4_addr="10.1.1.1/24"
                )
            ]
        )
    except ValidationError as e:
        handle_error
    ```
    """

    deploy: StrictBool = Field(default=True)
    export_evpn_rt: str = Field(default="")
    import_evpn_rt: str = Field(default="")
    ip_address: str
    vrf_lite: Optional[list[PlaybookVrfLiteModel]] = Field(default=None)

    @field_validator("ip_address", mode="before")
    @classmethod
    def validate_ip_address(cls, value: str) -> str:
        """
        Validate ip_address is an IPv4 host address without prefix.
        """
        if value != "":
            IPv4HostModel(ipv4_host=str(value))
        return value

    @field_validator("vrf_lite", mode="before")
    @classmethod
    def vrf_lite_set_to_none_if_empty_list(cls, value: Union[None, list]) -> Optional[list[PlaybookVrfLiteModel]]:
        """
        Set vrf_lite to None if it is an empty list.
        This mimics the behavior of the original code.
        """
        if not value:
            return None
        return value


class PlaybookVrfModelV12(BaseModel):
    """
    # Summary


    Model to validate a playbook VRF configuration.

    ## Raises

    - ValueError if:
        - Any field does not meet its validation criteria.

    ## Attributes:
        - adv_default_routes - boolean
        - adv_host_routes - boolean
        - attach - list of PlaybookVrfAttachModel
        - bgp_passwd_encrypt - int (BgpPasswordEncrypt enum value, 3, 7)
        - bgp_password - string
        - deploy - boolean
        - disable_rt_auto - boolean
        - export_evpn_rt - string
        - export_mvpn_rt - string
        - export_vpn_rt - string
        - import_evpn_rt - string
        - import_mvpn_rt - string
        - import_vpn_rt - string
        - ipv6_linklocal_enable - boolean
        - l3vni_wo_vlan - boolean
        - loopback_route_tag- integer range (0-4294967295)
        - max_bgp_paths - integer range (1-64)
        - max_ibgp_paths - integer range (1-64)
        - netflow_enable - boolean
        - nf_monitor - string
        - no_rp - boolean
        - overlay_mcast_group - string (IPv4 multicast group address without prefix)
        - redist_direct_rmap - string
        - v6_redist_direct_rmap - string
        - rp_address - string (IPv4 host address without prefix)
        - rp_external - boolean
        - rp_loopback_id - int range (0-1023)
        - service_vrf_template - string
        - static_default_route - boolean
        - trm_bgw_msite - boolean
        - trm_enable - boolean
        - underlay_mcast_ip - string (IPv4 multicast group address without prefix)
        - vlan_id - integer range (0-4094)
        - vrf_description - string
        - vrf_extension_template - string
        - vrf_id - integer range (0- 16777214)
        - vrf_int_mtu - integer range (68-9216)
        - vrf_intf_desc - string
        - vrf_name - string
        - vrf_template - string
        - vrf_vlan_name - string
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        use_enum_values=True,
        validate_assignment=True,
    )
    adv_default_routes: StrictBool = Field(default=True)  # advertiseDefaultRouteFlag
    adv_host_routes: StrictBool = Field(default=False)  # advertiseHostRouteFlag
    attach: Optional[list[PlaybookVrfAttachModel]] = None
    bgp_passwd_encrypt: BgpPasswordEncrypt = Field(default=BgpPasswordEncrypt.MD5.value)  # bgpPasswordKeyType
    bgp_password: str = Field(default="")  # bgpPassword
    deploy: StrictBool = Field(default=True)
    disable_rt_auto: StrictBool = Field(default=False)  # disableRtAuto
    export_evpn_rt: str = Field(default="")  # routeTargetExportEvpn
    export_mvpn_rt: str = Field(default="")  # routeTargetExportMvpn
    export_vpn_rt: str = Field(default="")  # routeTargetExport
    import_evpn_rt: str = Field(default="")  # routeTargetImportEvpn
    import_mvpn_rt: str = Field(default="")  # routeTargetImportMvpn
    import_vpn_rt: str = Field(default="")  # routeTargetImport
    ipv6_linklocal_enable: StrictBool = Field(default=True)  # ipv6LinkLocalFlag
    l3vni_wo_vlan: StrictBool = Field(default=False)  # enableL3VniNoVlan
    loopback_route_tag: int = Field(default=12345, ge=0, le=4294967295)  # tag
    max_bgp_paths: int = Field(default=1, ge=1, le=64)  # maxBgpPaths
    max_ibgp_paths: int = Field(default=2, ge=1, le=64)  # maxIbgpPaths
    netflow_enable: StrictBool = Field(default=False)  # ENABLE_NETFLOW
    nf_monitor: str = Field(default="")  # NETFLOW_MONITOR
    no_rp: StrictBool = Field(default=False)  # isRPAbsent
    overlay_mcast_group: str = Field(default="")  # multicastGroup
    redist_direct_rmap: str = Field(default="FABRIC-RMAP-REDIST-SUBNET")  # vrfRouteMap
    v6_redist_direct_rmap: str = Field(default="FABRIC-RMAP-REDIST-SUBNET") # v6VrfRouteMap
    rp_address: str = Field(default="")  # rpAddress
    rp_external: StrictBool = Field(default=False)  # isRPExternal
    rp_loopback_id: Optional[Union[int, str]] = Field(default="", ge=-1, le=1023)  # loopbackNumber
    service_vrf_template: Optional[str] = Field(default=None)  # serviceVrfTemplate
    source: Optional[str] = None
    static_default_route: StrictBool = Field(default=True)  # configureStaticDefaultRouteFlag
    trm_bgw_msite: StrictBool = Field(default=False)  # trmBGWMSiteEnabled
    trm_enable: StrictBool = Field(default=False)  # trmEnabled
    underlay_mcast_ip: str = Field(default="")  # L3VniMcastGroup
    vlan_id: Optional[int] = Field(default=None, le=4094)
    vrf_description: str = Field(default="")  # vrfDescription
    vrf_extension_template: str = Field(default="Default_VRF_Extension_Universal")  # vrfExtensionTemplate
    vrf_id: Optional[int] = Field(default=None, le=16777214)
    vrf_int_mtu: int = Field(default=9216, ge=68, le=9216)  # mtu
    vrf_intf_desc: str = Field(default="")  # vrfIntfDescription
    vrf_name: str = Field(..., min_length=1, max_length=32)  # vrfName
    vrf_template: str = Field(default="Default_VRF_Universal")
    vrf_vlan_name: str = Field(default="")  # vrfVlanName

    @field_validator("overlay_mcast_group", mode="before")
    @classmethod
    def validate_overlay_mcast_group(cls, value: str) -> str:
        """
        Validate overlay_mcast_group is an IPv4 multicast group address without prefix.
        """
        if value != "":
            IPv4MulticastGroupModel(ipv4_multicast_group=str(value))
        return value

    @field_validator("source", mode="before")
    @classmethod
    def hardcode_source_to_none(cls, value) -> None:
        """
        To mimic original code, hardcode source to None.
        """
        if value is not None:
            value = None
        return value

    @field_validator("rp_address", mode="before")
    @classmethod
    def validate_rp_address(cls, value: str) -> str:
        """
        Validate rp_address is an IPv4 host address without prefix.
        """
        if value != "":
            IPv4HostModel(ipv4_host=str(value))
        return value

    @field_validator("rp_loopback_id", mode="before")
    @classmethod
    def validate_rp_loopback_id_before(cls, value: Union[int, str]) -> Union[int, str]:
        """
        Validate rp_loopback_id is an integer between 0 and 1023.
        If it is an empty string, return -1.  This will be converted to "" in an "after" validator.
        """
        if isinstance(value, str) and value == "":
            return -1
        if not isinstance(value, int):
            raise ValueError(f"Invalid rp_loopback_id: {value}. It must be an integer between 0 and 1023.")
        if value < 0 or value > 1023:
            raise ValueError(f"Invalid rp_loopback_id: {value}. It must be an integer between 0 and 1023.")
        return value

    @field_validator("rp_loopback_id", mode="after")
    @classmethod
    def validate_rp_loopback_id_after(cls, value: Union[int, str]) -> Union[int, str]:
        """
        Convert rp_loopback_id to an empty string if it is -1.
        """
        if value == -1:
            return ""
        return value

    @field_validator("underlay_mcast_ip", mode="before")
    @classmethod
    def validate_underlay_mcast_ip(cls, value: str) -> str:
        """
        Validate underlay_mcast_ip is an IPv4 multicast group address without prefix.
        """
        if value != "":
            IPv4MulticastGroupModel(ipv4_multicast_group=str(value))
        return value

    @field_validator("vlan_id", mode="before")
    @classmethod
    def validate_vlan_id_before(cls, value: Union[int, str]) -> Union[int, str]:
        """
        Validate vlan_id is an integer between 2 and 4094.
        If it is "", return -1.  This will be converted to None in an "after" validator.
        """
        if isinstance(value, str) and value == "":
            return -1
        if isinstance(value, str):
            try:
                value = int(value)
            except (TypeError, ValueError) as error:
                msg = f"Invalid vlan_id: {value}. It must be an integer between 2 and 4094."
                msg += f" Error detail: {error}"
                raise ValueError(msg) from error
        if not isinstance(value, int):
            raise ValueError(f"Invalid vlan_id: {value}. It must be an integer between 2 and 4094.")
        if value < 2 or value > 4094:
            raise ValueError(f"Invalid vlan_id: {value}. It must be an integer between 2 and 4094.")
        return value

    @field_validator("vlan_id", mode="after")
    @classmethod
    def validate_vlan_id_after(cls, value: Union[int, str]) -> Union[int, str]:
        """
        Convert vlan_id to None if it is -1.
        """
        if value == -1:
            return None
        return value


class PlaybookVrfConfigModelV12(BaseModel):
    """
    Model for VRF playbook configuration.
    """

    config: list[PlaybookVrfModelV12] = Field(default_factory=list[PlaybookVrfModelV12])

class PlaybookParentFabricConfigModel(BaseModel):
    """
    # Summary

    Model for Parent MSD VRF configuration.
    This model validates VRF parameters specific to Parent MSD fabrics.

    ## Attributes:
        - vrf_id - integer range (0-16777214)
        - vlan_id - integer range (0-4094)
        - vrf_template - string
        - vrf_extension_template - string
        - vrf_vlan_name - string
        - vrf_intf_desc - string
        - vrf_description - string
        - vrf_int_mtu - integer range (68-9216)
        - loopback_route_tag - integer range (0-4294967295)
        - redist_direct_rmap - string
        - v6_redist_direct_rmap - string
        - max_bgp_paths - integer range (1-64)
        - max_ibgp_paths - integer range (1-64)
        - ipv6_linklocal_enable - boolean
        - disable_rt_auto - boolean
        - import_vpn_rt - string
        - export_vpn_rt - string
        - import_evpn_rt - string
        - export_evpn_rt - string
        - service_vrf_template - string (optional)
        - source - string (optional)
        - child_fabric_config - list of PlaybookChildFabricConfigModel
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        use_enum_values=True,
        validate_assignment=True,
    )
    
    # Required fields
    vrf_name: str = Field(..., min_length=1, max_length=32)
    
    # Optional fields with defaults
    vrf_id: Optional[int] = Field(default=None, le=16777214)
    vlan_id: Optional[int] = Field(default=None, le=4094)
    vrf_template: str = Field(default="Default_VRF_Universal")
    vrf_extension_template: str = Field(default="Default_VRF_Extension_Universal")
    vrf_vlan_name: str = Field(default="")
    vrf_intf_desc: str = Field(default="")
    vrf_description: str = Field(default="")
    vrf_int_mtu: int = Field(default=9216, ge=68, le=9216)
    loopback_route_tag: int = Field(default=12345, ge=0, le=4294967295)
    redist_direct_rmap: str = Field(default="FABRIC-RMAP-REDIST-SUBNET")
    v6_redist_direct_rmap: str = Field(default="FABRIC-RMAP-REDIST-SUBNET")
    max_bgp_paths: int = Field(default=1, ge=1, le=64)
    max_ibgp_paths: int = Field(default=2, ge=1, le=64)
    ipv6_linklocal_enable: StrictBool = Field(default=True)
    disable_rt_auto: StrictBool = Field(default=False)
    import_vpn_rt: str = Field(default="")
    export_vpn_rt: str = Field(default="")
    import_evpn_rt: str = Field(default="")
    export_evpn_rt: str = Field(default="")
    service_vrf_template: Optional[str] = Field(default=None)
    source: Optional[str] = Field(default=None)
    deploy: StrictBool = Field(default=True)
    
    # Attachments
    attach: Optional[list[PlaybookVrfAttachModel]] = None

    @field_validator('max_bgp_paths', 'max_ibgp_paths')
    @classmethod
    def validate_path_range(cls, v):
        if v is not None and (v < 1 or v > 64):
            raise ValueError('must be between 1 and 64')
        return v
    
    @field_validator('vrf_int_mtu')
    @classmethod
    def validate_mtu_range(cls, v):
        if v is not None and (v < 68 or v > 9216):
            raise ValueError('must be between 68 and 9216')
        return v
        
    @field_validator('loopback_route_tag')
    @classmethod
    def validate_tag_range(cls, v):
        if v is not None and (v < 0 or v > 4294967295):
            raise ValueError('must be between 0 and 4294967295')
        return v

class PlaybookChildFabricConfigModel(BaseModel):
    """
    # Summary

    Model for child fabric configuration in Parent MSD fabrics.

    ## Attributes:
        - fabric_name - string (required)
        - l3vni_wo_vlan - boolean
        - adv_default_routes - boolean
        - adv_host_routes - boolean
        - static_default_route - boolean
        - bgp_password - string
        - bgp_passwd_encrypt - int (3, 7)
        - netflow_enable - boolean
        - nf_monitor - string
        - trm_enable - boolean
        - no_rp - boolean
        - rp_address - string (IPv4 host address)
        - rp_external - boolean
        - rp_loopback_id - integer
        - underlay_mcast_ip - string (IPv4 multicast group)
        - overlay_mcast_group - string (IPv4 multicast group)
        - trm_bgw_msite - boolean
        - import_mvpn_rt - string
        - export_mvpn_rt - string
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        use_enum_values=True,
        validate_assignment=True,
    )
    fabric_name: str
    l3vni_wo_vlan: StrictBool = Field(default=False)
    adv_default_routes: StrictBool = Field(default=True)
    adv_host_routes: StrictBool = Field(default=False)
    static_default_route: StrictBool = Field(default=True)
    bgp_password: str = Field(default="")
    bgp_passwd_encrypt: BgpPasswordEncrypt = Field(default=BgpPasswordEncrypt.MD5.value)
    netflow_enable: StrictBool = Field(default=False)
    nf_monitor: str = Field(default="")
    trm_enable: StrictBool = Field(default=False)
    no_rp: StrictBool = Field(default=False)
    rp_address: str = Field(default="")
    rp_external: StrictBool = Field(default=False)
    rp_loopback_id: Optional[Union[int, str]] = Field(default="", ge=-1, le=1023)
    underlay_mcast_ip: str = Field(default="")
    overlay_mcast_group: str = Field(default="")
    trm_bgw_msite: StrictBool = Field(default=False)
    import_mvpn_rt: str = Field(default="")
    export_mvpn_rt: str = Field(default="")

    @field_validator("rp_address", mode="before")
    @classmethod
    def validate_rp_address(cls, value: str) -> str:
        """
        Validate rp_address is an IPv4 host address without prefix.
        """
        if value != "":
            IPv4HostModel(ipv4_host=str(value))
        return value

    @field_validator("overlay_mcast_group", mode="before")
    @classmethod
    def validate_overlay_mcast_group(cls, value: str) -> str:
        """
        Validate overlay_mcast_group is an IPv4 multicast group address without prefix.
        """
        if value != "":
            IPv4MulticastGroupModel(ipv4_multicast_group=str(value))
        return value

    @field_validator("underlay_mcast_ip", mode="before")
    @classmethod
    def validate_underlay_mcast_ip(cls, value: str) -> str:
        """
        Validate underlay_mcast_ip is an IPv4 multicast group address without prefix.
        """
        if value != "":
            IPv4MulticastGroupModel(ipv4_multicast_group=str(value))
        return value

    @field_validator("rp_loopback_id", mode="before")
    @classmethod
    def validate_rp_loopback_id_before(cls, value: Union[int, str]) -> Union[int, str]:
        """
        Validate rp_loopback_id is an integer between 0 and 1023.
        If it is an empty string, return -1. This will be converted to "" in an "after" validator.
        """
        if isinstance(value, str) and value == "":
            return -1
        if not isinstance(value, int):
            try:
                value = int(value)
            except (TypeError, ValueError) as error:
                msg = f"Invalid rp_loopback_id: {value}. It must be an integer between 0 and 1023."
                msg += f" Error detail: {error}"
                raise ValueError(msg) from error
        if value < 0 or value > 1023:
            raise ValueError(f"Invalid rp_loopback_id: {value}. It must be an integer between 0 and 1023.")
        return value

    @field_validator("rp_loopback_id", mode="after")
    @classmethod
    def validate_rp_loopback_id_after(cls, value: Union[int, str]) -> Union[int, str]:
        """
        Convert rp_loopback_id to an empty string if it is -1.
        """
        if value == -1:
            return ""
        return value