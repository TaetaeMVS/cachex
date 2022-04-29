import sys
import numpy as np
np.set_printoptions(threshold=sys.maxsize)
import random
import string

import config
from stable_baselines3.common.logger import Logger, configure
from stable_baselines3.common.policies import obs_as_tensor

# predict_proba function taken from https://stackoverflow.com/questions/66428307/how-to-get-action-propability-in-stable-baselines-3
def predict_proba(model, state):
    obs = model.policy.obs_to_tensor(state)[0]
    dis = model.policy.get_distribution(obs)
    probs = dis.distribution.probs
    probs_np = probs.detach().cpu().numpy()
    return probs_np[0].astype('float64')

def sample_action(action_probs):
    action = np.random.multinomial(len(action_probs), pvals = action_probs)
    return action[0]


def mask_actions(legal_actions, action_probs):
    legal_actions = np.array(legal_actions)
    legal_actions = np.resize(legal_actions, action_probs.shape)
    masked_action_probs = np.multiply(legal_actions, action_probs)
    masked_action_probs = masked_action_probs / np.sum(masked_action_probs)
    return masked_action_probs





class Agent():
  def __init__(self, name, model = None):
      self.name = name
      self.id = self.name + '_' + ''.join(random.choice(string.ascii_lowercase) for x in range(5))
      self.model = model
      self.points = 0

  def print_top_actions(self, action_probs):
    top5_action_idx = np.argsort(-action_probs)[:5]
    # print(action_probs)
    # print(top5_action_idx)
    top5_actions = action_probs[top5_action_idx]
    Logger = configure(config.LOGDIR)
    print(f"Top 5 actions: {[str(i) + ': ' + str(round(a,2))[:5] for i,a in zip(top5_action_idx, top5_actions)]}")

  def choose_action(self, env, choose_best_action, mask_invalid_actions):
      Logger = configure(config.LOGDIR) 
      if self.name == 'rules':
        action_probs = np.array(env.get_possible_actions(env.state))
        value = None
      else:
        action_probs = predict_proba(self.model, env.state).astype('float64')
        value = self.model.predict(obs_as_tensor(env.state, device = "cuda").cpu())[0]
        # policy_pi.value(np.array([env.observation]))[0]
        Logger.info(Logger, value)

      self.print_top_actions(action_probs)
      
      if mask_invalid_actions:
        action_probs = mask_actions(env.get_possible_actions(env.state), action_probs)
        Logger.debug('Masked ->')
        self.print_top_actions(action_probs)
        
      action = np.argmax(action_probs)
      Logger.debug(f'Best action {action}')

      if not choose_best_action:
          action = sample_action(action_probs)
          Logger.debug(f'Sampled action {action} chosen')

      return action



