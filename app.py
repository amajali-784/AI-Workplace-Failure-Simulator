from env.environment import WorkplaceEnv


def app():
    env = WorkplaceEnv()
    obs = env.reset()
    return {"status": "ok", "message": obs.message}

