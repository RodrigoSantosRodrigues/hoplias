#!/bin/sh

ollama serve &

while ! nc -z localhost 11434; do
  echo "Waiting for Ollama to start..."
  sleep 1
done

if nvidia-smi > /dev/null 2>&1; then
    echo ">>> GPU detected - Loading GPU models..."
    MODEL_FILE="/root/models-gpu.txt"
    export OLLAMA_CUDA=1
else
    echo ">>> No GPU detected - Loading CPU models..."
    MODEL_FILE="/root/models-cpu.txt"
fi

while read model; do
    echo ">> Pulling model: $model"
    for i in 1 2 3; do
        if timeout 300 ollama pull $model; then
            echo "Successfully pulled $model"
            break
        else
            echo "Attempt $i/3 failed for $model"
            [ $i -eq 3 ] && echo "Failed to pull $model after 3 attempts"
            sleep 5
        fi
    done
done < $MODEL_FILE

wait
