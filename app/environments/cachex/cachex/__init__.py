from gym.envs.registration import register

register(
    id='Cachex-v0',
    entry_point='cachex.envs:HexEnv',
)

