# Эталонное решение ДЭ БУ 09.02.08 (КИМ 09.02.08-1-2027) — «Умный перекрёсток»

## Структура
```
bin/         скрипты запуска; базы данных SQLite создаются программами здесь
obj/         временные файлы сборки
resources/   графика из архива Прил_1 (без изменений), схема и скриншоты
src/
  city/      Задания 1 и 3: виртуальная сеть «Умный перекрёсток», обучение Q-learning
  module/    Задание 2: прошивка Arduino модуля «Шлагбаум»
  gate/      Задание 2: управляющая программа, база событий
  db/        скрипты создания баз данных
  scheme/    файл схемы изделия (на экзамене — проект Fritzing / Tinkercad)
Presentation.pptx, Instruction.docx — Задание 1; Diagnostics.pptx — Задание 2
```

## Задание 1. «Умный перекрёсток» — рабочее пространство для испытания ИИ
- Запуск: bin/run_city.bat (исходники: src/city/city.py, форма: src/city/city.ui)
- Графика: resources, иконка: resources/media/GCicon.ico
- Характеристики выбираются из выпадающих списков; R — повернуть объект или переключить светофор; Delete — удалить
- Схема изделия: resources/scheme.png; скриншот: resources/screenshot.png
- Презентация: Presentation.pptx; инструкция пользователя: Instruction.docx
- Пример готовой сети: src/city/demo_network.json (кнопка «Открыть сеть…»)

## Задание 2. Модуль «Шлагбаум» «Умного перекрёстка»
- Прошивка: src/module/module.ino (Arduino Uno; серво D9, DHT11 D2, фоторезистор A0, HC-SR04 D7/D6)
- Запуск: bin/run_gate.bat (исходники: src/gate/gate.py, форма: src/gate/gate.ui)
- База данных: bin/events.db, структура: src/db/schema.sql
- Скриншот: resources/screenshot_gate.png; презентация о выявлении неисправностей: Diagnostics.pptx
- Команды ПК -> Arduino: M, A, O, C, T, R
- Данные Arduino -> ПК: DATA;режим;шлагбаум;расстояние;температура;влажность;свет;день;статус

## Задание 3. Обучение автомобиля в «Умном перекрёстке»
- Обучение: Q-learning (обучение с подкреплением), параметры — эпизоды, α, γ
- База данных: bin/training.db (таблицы runs и episodes), схема: src/db/training_schema.sql
- Запуск: bin/run_city.bat; скриншот: resources/screenshot_training.png

## Требования
Python 3.8+, PyQt5, pyserial (requirements.txt).
