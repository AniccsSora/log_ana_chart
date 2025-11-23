
DEFAULT_TIMEOUT = 120

diag_cmd_def = {
    "diag_tool_info":               {
        "index":1,
        "timeout": DEFAULT_TIMEOUT,
        },
    "diag_main_chip_gpio":          {
        "index":2,
        "timeout": DEFAULT_TIMEOUT,
        },
    "diag_cpld_gpio":               {
        "index":3,
        "timeout": DEFAULT_TIMEOUT,
        },
    "diag_sfp_low_speed":           {
        "index":4,
        "timeout": 300,
        },
    "diag_system_led":              {
        "index":5,
        "timeout": DEFAULT_TIMEOUT,
        },
    "diag_copper_port_led":         {
        "index":6,
        "timeout": DEFAULT_TIMEOUT,
        },
    "diag_fiber_port_led":          {
        "index":7,
        "timeout": DEFAULT_TIMEOUT,
        },
    "diag_phy_mdc_mdio":            {
        "index":8,
        "timeout": DEFAULT_TIMEOUT,
        },
    "diag_sfp_control_pin":         {
        "index":9,
        "timeout": 300,
        },
    "diag_rtc_info":                {
        "index":10,
        "timeout": DEFAULT_TIMEOUT,
        },
    "diag_thermal_sensor":          {
        "index":11,
        "timeout": DEFAULT_TIMEOUT,
        },
    "diag_mcu_info":                {
        "index":12,
        "timeout": DEFAULT_TIMEOUT,
        },
    "diag_eeprom_info":             {
        "index":13,
        "timeout": DEFAULT_TIMEOUT,
        },
    "diag_sfp_i2c_access":          {
        "index":14,
        "timeout": DEFAULT_TIMEOUT,
        },
    "diag_poe_load":                {
        "index":15,
        "timeout": DEFAULT_TIMEOUT,
        },
    "diag_i2c_device_access":       {
        "index":16,
        "timeout": DEFAULT_TIMEOUT,
        },
    "diag_cpu_info":                {
        "index":17,
        "timeout": DEFAULT_TIMEOUT,
        },
    "diag_cpu_stress_test":         {
        "index":18, 
        "timeout": DEFAULT_TIMEOUT,
        },
    "diag_memory_stress_test":      {
        "index":19,
        "timeout": DEFAULT_TIMEOUT,
        },
    "diag_memory_size":             {
        "index":20,
        "timeout": DEFAULT_TIMEOUT,
        },
    "diag_nor_os_info":             {
        "index":21,
        "timeout": DEFAULT_TIMEOUT,
        },
    "diag_interrupt_for_system":    {
        "index":22,
        "timeout": DEFAULT_TIMEOUT,
        },
    "diag_interrupt_for_phy":       {
        "index":23,
        "timeout": DEFAULT_TIMEOUT,
        },
    "diag_usb_storage":             {
        "index":24,
        "timeout": DEFAULT_TIMEOUT,
        },
    "diag_eusb_storage":            {
        "index":25,
        "timeout": DEFAULT_TIMEOUT,
        },
    "diag_dpll_info":               {
        "index":26,
        "timeout": DEFAULT_TIMEOUT,
        },
    "diag_copper_speed":            {
        "index":27,
        "timeout": DEFAULT_TIMEOUT,
        },
    "diag_copper_traffic":          {
        "index":28,
        "timeout": DEFAULT_TIMEOUT,
        },
    "diag_fiber_traffic":           {
        "index":29,
        "timeout": DEFAULT_TIMEOUT,
        },
    "diag_all_port_traffic":        {
        "index":30,
        "timeout": DEFAULT_TIMEOUT,
        },
    "diag_combo_prefer_media":      {
        "index":31,
        "timeout": DEFAULT_TIMEOUT,
        },
    "diag_cpld_info":               {
        "index":32,
        "timeout": DEFAULT_TIMEOUT,
        },
    "pn_sn_info":                   {
        "index":33,
        "timeout": DEFAULT_TIMEOUT,
        },
    "diag_emp_access_test":         {
        "index":34,
        "timeout": DEFAULT_TIMEOUT,
        },
    "diag_dpll_ref_clk":            {
        "index":35,
        "timeout": DEFAULT_TIMEOUT,
        },
    "diag_tod_device":              {
        "index":36, 
        "timeout": DEFAULT_TIMEOUT,
        },
    "diag_thermal_display":         {
        "index":37,
        "timeout": DEFAULT_TIMEOUT,
        },
}



def get_diag_cmd_index(cmd_name: str) -> int:
    return diag_cmd_index.get(cmd_name, -1)


