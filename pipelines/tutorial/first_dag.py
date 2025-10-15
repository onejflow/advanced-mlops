from datetime import datetime, timedelta
from textwrap import dedent

import pendulum
from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import DAG

from utils.callbacks import failure_callback, success_callback

local_timezone = pendulum.timezone("Asia/Seoul")

with DAG(
    # TODO: "simple_dag"이라는 이름의 DAG 설정
    dag_id="simple_dag",
    # TODO: default_args에는 다음 내용이 들어감
    # TODO: "user" 사용자가 소유한 DAG / 본인의 이메일 / 실패 및 재시도 시 이메일 알림 여부
    # TODO: 재시도 1회 / 재시도 간격 5분
    # TODO: 실패 시 callback (failure_callback) / 성공 시 callback (success_callback)
    default_args={
        "owner": "wj", # project 작업자 
        "depends_on_past": False, # 과거의 성공여부에 따라서 사용할지 말지 정하는것
        "email": "onej.flow@gmail.com",
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        "on_failure_callback": failure_callback, # 호출가능한 객체 적용 가능
        "on_success_callback": success_callback,
    },
    description="Simple airflow dag",
    schedule="0 15 * * *",
    start_date=datetime(2025, 10, 1, tzinfo=local_timezone),
    catchup=False, # 이전에 실패하면 실패한것까지 다 실행
    tags=set(["lgcns", "mlops"]),
) as dag:
    task1 = BashOperator(
        task_id="print_date",
        # TODO: 현재 시간을 출력하는 bash_command 입력
        bash_command="date",
    )
    task2 = BashOperator(
        task_id="sleep",
        depends_on_past=False,
        # TODO: 5초 sleep하는 bash_command를 입력하고 3회 재시도하도록 설정
        bash_command="sleep 3",
        retries=3,
    )
    # jinja template 예시
    loop_command = dedent(
        """
        {% set kst_ds = data_interval_start.in_timezone('Asia/Seoul').to_date_string() %}
        {% for i in range(5) %}
            echo "ds = {{ kst_ds }}"
            echo "macros.ds_add(ds, {{ i }}) = {{ macros.ds_add(kst_ds, i) }}"
        {% endfor %}
        """
    )
    task3 = BashOperator(
        task_id="print_with_loop",
        bash_command=loop_command,
    )
    task4 = BashOperator(
        task_id="print_yes",
        bash_command="echo yes",
    )
    
    task1 >> [task2, task3]
    task2 >> task4
