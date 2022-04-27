
from stable_baselines3 import A2C
from cachex import HexEnv

env = HexEnv()
model = A2C('MlpPolicy', env, verbose=1).learn(total_timesteps=1000)
model.save("cachex_a2c")