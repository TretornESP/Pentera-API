from app.service.pentera.pentera import PenteraService, UnauthorizedException
from app.service.pentera.config import config
import time 

def pentera(conf=config):
    if conf is None:
        print("[PENTERA] Invalid configuration file, aborting")
        return []

    try:
        testing_scenarios = PenteraService.get_testing_scenarios()
    except UnauthorizedException as e:
        conf.log.error("[PENTERA] [RUNNER] [EXCEPTION] UnauthorizedException: {}".format(e))
        PenteraService.login()
        testing_scenarios = PenteraService.get_testing_scenarios()
        return []

    crack_result = []
    for testing_scenario in testing_scenarios:
        if testing_scenario.name == config.get('TARGET_SCENARIO'):
            conf.log.info("[PENTERA] [RUNNER] Starting scenario: {}".format(testing_scenario.name) + ". This may take a while...")
            started_scenario = PenteraService.start_testing_scenario(testing_scenario.template_id)
            if len(started_scenario) == 0:
                conf.log.error("[PENTERA] [RUNNER] No task runs started")     
                return []
            
            started_task = started_scenario[0]
            start_time = int(started_task.start_time - 1000)
            conf.log.info("[PENTERA] [RUNNER] Task {} started at {}".format(started_task.task_run_id, start_time))

            finish = False
            target_task = None
            while not finish:
                end_time = round(time.time() * 1000)
                conf.log.info("[PENTERA] [RUNNER] [{}] Waiting for task {} to finish, this may take a really long time...".format(end_time, started_task.task_run_id))
                if (end_time - start_time) > config.get("MAX_WAIT_MILLIS"):
                    conf.log.critical("[PENTERA] [RUNNER] Timeout reached, sorry bud...")
                    return []
                task_runs = PenteraService.get_testing_history(start_time, end_time)
                for task in task_runs:
                    if task.task_run_id == started_task.task_run_id and task.end_time is not None:
                        target_task = task
                        finish = True

                time.sleep(30)

            conf.log.info("[PENTERA] [RUNNER] Task {} completed, duration: {}. Extracting results...".format(target_task.name, target_task.duration))
            
            achievements = PenteraService.get_testing_achievements(target_task.task_run_id, config.get("ACHIEVEMENT_NAME"))
            cracked_users = []
            for achievement in achievements:
                cracked_users.append(achievement.parameters[0].split(',')[0].split(': ')[1])

            crack_result.append(cracked_users)
    return crack_result