function assert_env_value {
  variable_name=$1
  if [[ "${!variable_name}" == "" ]]
  then
    echo must provide $variable_name in $0 1>&2
    exit 1
  fi
}

function assert_env {
  # asserts the variables that used outside the entry points
  assert_env_value _SECURITY_CAMERA_CONFIG
  assert_env_value _SECURITY_CAMERA_DATA
  assert_env_value GPIOZERO_PIN_FACTORY
}
