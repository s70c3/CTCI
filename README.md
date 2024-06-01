CTCI
==============================

Clumped texture composite images projects (froath, rocks and other texture images)

Project Organization
------------

    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── docs               <- A default Sphinx project; see sphinx-doc.org for details
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │   └── make_dataset.py
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   └── build_features.py
    │   │
    │   ├── models         <- Scripts to train models and then use trained models to make
    │   │   │                 predictions
    │   │   ├── predict_model.py
    │   │   └── train_model.py
    │   │
    │   └── visualization  <- Scripts to create exploratory and results oriented visualizations
    │       └── visualize.py
    │
    └── tox.ini            <- tox file with settings for running tox; see tox.readthedocs.io



--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>

 Установка

# Слабая разметка

Слабая разметка однородных данных реализована с использованием нейронных сетей YOLOv8 и Segment Anything, а также с помощью алгоритма сегментации водоразделом.

Функционал слабой разметки расположен в модуле `src/data/weakly_segmentation/annotation.py` в методе `annotation`. Разметка выполняется для указанной в аргументах папки с данными

Пример использования:

```python
import sys

from src.data.weakly_segmentation.annotation import annotation


data_dir = sys.argv[1]  # Директория с неразмеченными данными
folder = sys.argv[2]    # Папка, с неразмеченными данными

custom_yolo_checkpoint_path = sys.argv[3]  # Путь до весов модели YOLOv8
sam_checkpoint = sys.argv[4]  # Путь до весов модели SAM
sam_model_type = sys.argv[5]  # Тип модели SAM

narrowing = 0.20  # Значение сужения масок сегменатации. Предотвращает сливание масок однородных объектов
erode_iterations = 1  # Количество итераций эрозии 
processes_num = 3  # Количество параллельных процессов сегментации изображений
prompt_points = False  # Использование точек в промпте SAM

device = "cpu"  # Девайс, на котором выполняется разметка

annotation(
    data_dir, folder,
    custom_yolo_checkpoint_path, sam_checkpoint, sam_model_type, narrowing=narrowing,
    erode_iterations=erode_iterations, processes_num=processes_num, prompt_points=prompt_points,
    device=device
)

```

# Самообучение

# Сегментация

## Конфигурационные файлы

Для удобства обучения и использования моделей, мы используем конфигурационные файлы, примеры которых можно найти в директории `src/infrastructure/configs` . Мы рекомендуем придерживаться структуры, указанной в них.

## Модели сегментации

Для сегментации изображений однородных данных добавлены такие модели, как: Yolov8, SegFormer, Swin+UNETR, DeepLabv3, HRNet. Данные модели расположены в директориях `src/models/<название модели>` . 

Возможна инициализация модели с помощью соответствующего класса, например:

```python
net = transformers.SegformerForSemanticSegmentation.from_pretrained(
    f"nvidia/{model_name}-{model_type}-finetuned-ade-512-512",
    num_labels=1,
    image_size=image_size_height,
    ignore_mismatched_sizes=True
)

segformer = SegFormer(
    net=net, mask_head=final_layer, loss_fn=loss_fn,
    image_size=image_size, device=device
)

# Все модели сегментации наследуются от одного класса BaseModel
```

либо, с помощью метода `build_<название модели>`, например:

```python
 config_handler = read_yaml_config(config_path) # обработчик конфигурационных файлов
 model = build_segformer(config_handler)
```

## Обучение моделей

Для обучения или дообучения моделей добавлен класс тренировщика `Trainer` , расположенный в модуле `src/models/train.py` :

```python
trainer = Trainer(
    model=model,
    optimizer=optimizer,
    scheduler=scheduler,
    metrics=metrics,
    main_metric_name=main_metric_name,
    save_dir=model_save_dir,
    device=device
)
```

В директории `src/infrastructure/models_tracking`  расположены скрипты, позволяющие обучить или дообучить модели “из коробки” с использованием конфигурационного файла. Пример использования:

```bash
python src/infrastructure/models_tracking/segformer_tracking.py <config_path>
```

### ADELE
Библиотека поддерживает [Adaptive Early-Learning Correction for Segmentation from Noisy Annotations](https://arxiv.org/abs/2110.03740). Для использования достаточно создать датасет **без аугментаций**, то есть без афинных преобразований, но в том виде, в котором модель будет получать изображения на инференсе. В класс тренировщика необходимо будет передавать отдельно инициализированный датасет из тренировочных файлов. В файле конфигураций необходимо добавить шаг, через который будет применяться метод. 

```python
# В файле трекинга добавить следующие строки

from src.models.utils.config import read_yaml_config
from src.features.segmentation.dataset import get_train_dataset_by_config

config_handler = read_yaml_config(config_path)
adele_dataset = get_train_dataset_by_config(
        config_handler,
        transform=tr, # стандартные преобразования
        augmentation_transform=None
    )
adele_dataset.return_names = True
```




# Экспорт в ONNX

Описанные выше модели могут быть экспортированы в onnx формат для дальнейшего запуска в любом окружении, поддерживающем onnx-runtime. 

Экспорт каждой из моделей можно выполнить с использованием заготовленных скриптов, расположенных в директории `src/infrastructure/models_inference` . Например:

```bash
python src/infrastructure/models_inference/segformer_export.py <config_path>
```

Код конвертации и квантизации можно найти в модуле `src/models/inference.py` .