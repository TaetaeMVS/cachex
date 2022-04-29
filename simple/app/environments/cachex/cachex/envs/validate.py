from stable_baselines3.common.env_checker import check_env
from cachex import HexEnv
env = HexEnv()
check_env(env, warn = True)