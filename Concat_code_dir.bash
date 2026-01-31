(
  echo "===== Concat of Nash personal code projects ====="
  for dir in bdh pathway cookiecutter-pathway ai_lib bdh_code_editor nanoGPT nanochat micrograd llama2.c android-utils Bible-kjv JesusAI MosesAI AbrahamAI TrintityAI opencode iBS_LIB ChatGPT DBChildAI_Linux gpt-2 gpt-2-output-dataset gpt-3 GPT-3-Encoder gpt4all models.dev models.dev FamilyWeb gpt-discord-bot XGPT opencode-sdk-python code/openai-quickstart-python AI Voice bot reseach; do
    if [ -d "../$dir" ]; then
      echo -e "\n\n===== Directory: $dir ====="
      find "../$dir" -type f \( -name "*.py" -o -name "*.cpp" -o -name "*.h" -o -name "*.hpp" -o -name "*.c" -o -name "*.go" -o -name "*.rs" -o -name "*.kt" -o -name "*.sh" -o -name "CMakeLists.txt" -o -name "*.md" \) \
        -not -path "*/\.git/*" -not -path "*/build/*" -not -path "*/venv/*" -not -path "*/__pycache__/*" \
        -exec sh -c 'echo "\n----- {} -----"; cat "{}"; echo "\n"' \;
    fi
  done
) > input_code.txt

echo "Done. Size:" $(du -sh input_code.txt | cut -f1)
  
