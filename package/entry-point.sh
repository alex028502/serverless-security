# take environment variables expected by the entry points
# and create the environment expected by all the subprograms

source $package_dir/assert-env.sh

assert_env_value SECURITY_CAMERA_HOME
assert_env_value SECURITY_CAMERA_VENV
assert_env_value GPIOZERO_PIN_FACTORY

source $SECURITY_CAMERA_VENV/bin/activate
export _SECURITY_CAMERA_CONFIG=$SECURITY_CAMERA_HOME/config
export _SECURITY_CAMERA_DATA=$SECURITY_CAMERA_HOME/data

assert_env
