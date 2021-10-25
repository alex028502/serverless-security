def env_with_extended_path(env, *additional_paths):
    return dict(env, PATH=":".join(list(additional_paths) + [env["PATH"]]))
