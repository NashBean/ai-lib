#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <sys/stat.h>
#include <unistd.h>
#include <errno.h>
#include <time.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <sys/stat.h>
#include <unistd.h>
#include <errno.h>
#include <time.h>
// v0.5.0

// Max path length
#define MAX_PATH 4096
// Report file name
#define REPORT_FILE "code_base_report_v4.txt"
// Patch file for edits
#define PATCH_FILE "auto_patch.txt"
// Focused projects
const char *focus_projects[] = {
    "AbrahamAI",
    "MosesAI",
    "JesusAI",
    "ai_lib",
    "TrinityAI",
    "BDH",
    "iBS_LIB",
    NULL
};

// File type descriptions
const char *get_file_description(const char *filename) {
    const char *ext = strrchr(filename, '.');
    if (ext == NULL) return "Unknown file type (no extension)";
    if (strcmp(ext, ".py") == 0) return "Python script – likely core AI logic, server, or utils";
    if (strcmp(ext, ".json") == 0) return "JSON file – config, manifest, or data (e.g., knowledge base)";
    if (strcmp(ext, ".yaml") == 0 || strcmp(ext, ".yml") == 0) return "YAML file – API spec or config (e.g., openapi.yaml)";
    if (strcmp(ext, ".db") == 0) return "SQLite database – knowledge storage for AI";
    if (strcmp(ext, ".config") == 0) return "Config file – AI settings (e.g., port, DB file)";
    if (strcmp(ext, ".png") == 0) return "Image file – logo or visual asset";
    if (strcmp(ext, ".txt") == 0) return "Text file – logs, README, or notes";
    if (strcmp(ext, ".cpp") == 0 || strcmp(ext, ".h") == 0) return "C/C++ source/header – console or low-level utils";
    if (strcmp(ext, ".sh") == 0) return "Bash script – build or run helper";
    if (strcmp(ext, ".md") == 0) return "Markdown file – README or docs";
    if (strcmp(ext, ".gitignore") == 0) return "Git ignore file – excludes temp files from repo";
    if (strcmp(ext, ".git") == 0) return "Git repo directory – version control";
    return "Other file type – check manually";
}

// Function to check if a path is a directory
int is_directory(const char *path) {
    struct stat statbuf;
    if (stat(path, &statbuf) != 0) return 0;
    return S_ISDIR(statbuf.st_mode);
}

// Function to fetch and print file content snippet (first 200 lines)
void fetch_file_content(const char *path, FILE *report_fp) {
    FILE *file = fopen(path, "r");
    if (file == NULL) {
        fprintf(report_fp, "Error: Could not open file %s for fetching (errno: %d)\n", path, errno);
        return;
    }
    fprintf(report_fp, "Content Snippet (first 200 lines):\n");
    char line[1024];
    int line_count = 0;
    while (fgets(line, sizeof(line), file) != NULL && line_count < 200) {
        fprintf(report_fp, "%s", line);
        line_count++;
    }
    if (line_count == 200) fprintf(report_fp, "[Truncated – full file larger than snippet]\n");
    fclose(file);
    fprintf(report_fp, "\n");
}

// Simple auto-edit: Generates a basic diff patch suggestion based on instruction (placeholder – expand as needed)
void auto_edit(const char *instruction, FILE *patch_fp) {
    // Example: Parse simple instruction like "add try-except to add_todo in main.py"
    // This is basic – for real edits, use a tool like sed or full parser
    fprintf(patch_fp, "--- main.py (original)\n");
    fprintf(patch_fp, "+++ main.py (edited)\n");
    fprintf(patch_fp, "@@ -1,1 +1,1 @@\n");
    fprintf(patch_fp, "-# Old code\n");
    fprintf(patch_fp, "+# New code with %s\n", instruction);
    fprintf(patch_fp, "\nApply with patch main.py < %s\n", PATCH_FILE);
}

// Recursive function to traverse and report on directories/files
void traverse_dir(const char *base_path, FILE *report_fp, int depth, int is_focus, int fetch_content) {
    DIR *dir;
    struct dirent *entry;
    char path[MAX_PATH];
    struct stat statbuf;

    if (!(dir = opendir(base_path))) {
        fprintf(report_fp, "Error: Could not open directory %s (errno: %d)\n", base_path, errno);
        return;
    }

    while ((entry = readdir(dir)) != NULL) {
        if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0) continue;

        snprintf(path, sizeof(path), "%s/%s", base_path, entry->d_name);

        if (stat(path, &statbuf) == -1) {
            fprintf(report_fp, "Error: Could not stat %s (errno: %d)\n", path, errno);
            continue;
        }

        // Indent based on depth
        for (int i = 0; i < depth; i++) fprintf(report_fp, "  ");

        // File/Folder name and basic info
        time_t mod_time = statbuf.st_mtime;
        char time_str[64];
        strftime(time_str, sizeof(time_str), "%Y-%m-%d %H:%M:%S", localtime(&mod_time));
        fprintf(report_fp, "%s (Size: %ld bytes, Modified: %s) – ", entry->d_name, statbuf.st_size, time_str);

        if (is_directory(path)) {
            fprintf(report_fp, "Directory – Contains sub-files/folders for AI components.\n");
            // Recurse
            traverse_dir(path, report_fp, depth + 1, is_focus, fetch_content);
        } else {
            fprintf(report_fp, "%s\n", get_file_description(entry->d_name));
            if (fetch_content) {
                fetch_file_content(path, report_fp);
            }
        }
    }
    closedir(dir);
}

int main(int argc, char *argv[]) {
    int fetch_content = 0;
    int edit_mode = 0;
    char *edit_instruction = NULL;

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--fetch") == 0) {
            fetch_content = 1;
            printf("Fetching content snippets enabled.\n");
        } else if (strcmp(argv[i], "--edit") == 0 && i + 1 < argc) {
            edit_mode = 1;
            edit_instruction = argv[i + 1];
            i++;  // Skip next arg
            printf("Auto-edit mode enabled with instruction: %s\n", edit_instruction);
        }
    }

    const char *root_dir = "/code";  // Your local code base root
    FILE *report_fp = fopen(REPORT_FILE, "w");
    if (report_fp == NULL) {
        printf("Error: Could not open report file %s (errno: %d)\n", REPORT_FILE, errno);
        return 1;
    }

    fprintf(report_fp, "Code Base Report for Biblical Figure Knowledge AIs + Supports\n");
    fprintf(report_fp, "Generated: %s\n", asctime(localtime(&(time_t){time(NULL)})));
    fprintf(report_fp, "Root: %s\n\n", root_dir);

    // Traverse root, focus on specified projects
    DIR *root;
    struct dirent *entry;
    char path[MAX_PATH];

    if (!(root = opendir(root_dir))) {
        fprintf(report_fp, "Error: Could not open root %s (errno: %d)\n", root_dir, errno);
        fclose(report_fp);
        return 1;
    }

    while ((entry = readdir(root)) != NULL) {
        if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0) continue;

        snprintf(path, sizeof(path), "%s/%s", root_dir, entry->d_name);

        if (is_directory(path)) {
            int is_focus = 0;
            for (int i = 0; focus_projects[i] != NULL; i++) {
                if (strcmp(entry->d_name, focus_projects[i]) == 0) {
                    is_focus = 1;
                    break;
                }
            }

            if (is_focus) {
                fprintf(report_fp, "Focused Project: %s\n", entry->d_name);
                traverse_dir(path, report_fp, 1, is_focus, fetch_content);
                fprintf(report_fp, "\n");
            } else {
                fprintf(report_fp, "Other Project: %s (skipping details, but exists)\n", entry->d_name);
            }
        }
    }

    closedir(root);
    fclose(report_fp);

    // If edit mode, generate patch
    if (edit_mode && edit_instruction) {
        FILE *patch_fp = fopen(PATCH_FILE, "w");
        if (patch_fp == NULL) {
            printf("Error: Could not open patch file %s (errno: %d)\n", PATCH_FILE, errno);
            return 1;
        }
        auto_edit(edit_instruction, patch_fp);
        fclose(patch_fp);
        printf("Patch suggestion generated in %s. Apply as needed.\n", PATCH_FILE);
    }

    printf("Report generated in %s. Open it to view details.\n", REPORT_FILE);
    return 0;
}
// Max path length
#define MAX_PATH 4096
// Report file name
#define REPORT_FILE "code_base_report_v3.txt"
// Focused projects
const char *focus_projects[] = {
    "AbrahamAI",
    "MosesAI",
    "JesusAI",
    "ai_lib",
    "TrinityAI",
    "BDH",
    "iBS_LIB",
    NULL
};

// File type descriptions
const char *get_file_description(const char *filename) {
    const char *ext = strrchr(filename, '.');
    if (ext == NULL) return "Unknown file type (no extension)";
    if (strcmp(ext, ".py") == 0) return "Python script – likely core AI logic, server, or utils";
    if (strcmp(ext, ".json") == 0) return "JSON file – config, manifest, or data (e.g., knowledge base)";
    if (strcmp(ext, ".yaml") == 0 || strcmp(ext, ".yml") == 0) return "YAML file – API spec or config (e.g., openapi.yaml)";
    if (strcmp(ext, ".db") == 0) return "SQLite database – knowledge storage for AI";
    if (strcmp(ext, ".config") == 0) return "Config file – AI settings (e.g., port, DB file)";
    if (strcmp(ext, ".png") == 0) return "Image file – logo or visual asset";
    if (strcmp(ext, ".txt") == 0) return "Text file – logs, README, or notes";
    if (strcmp(ext, ".cpp") == 0 || strcmp(ext, ".h") == 0) return "C/C++ source/header – console or low-level utils";
    if (strcmp(ext, ".sh") == 0) return "Bash script – build or run helper";
    if (strcmp(ext, ".md") == 0) return "Markdown file – README or docs";
    if (strcmp(ext, ".gitignore") == 0) return "Git ignore file – excludes temp files from repo";
    if (strcmp(ext, ".git") == 0) return "Git repo directory – version control";
    return "Other file type – check manually";
}

// Function to check if a path is a directory
int is_directory(const char *path) {
    struct stat statbuf;
    if (stat(path, &statbuf) != 0) return 0;
    return S_ISDIR(statbuf.st_mode);
}

// Function to fetch and print file content snippet (first 200 lines)
void fetch_file_content(const char *path, FILE *report_fp) {
    FILE *file = fopen(path, "r");
    if (file == NULL) {
        fprintf(report_fp, "Error: Could not open file %s for fetching (errno: %d)\n", path, errno);
        return;
    }
    fprintf(report_fp, "Content Snippet (first 200 lines):\n");
    char line[1024];
    int line_count = 0;
    while (fgets(line, sizeof(line), file) != NULL && line_count < 200) {
        fprintf(report_fp, "%s", line);
        line_count++;
    }
    if (line_count == 200) fprintf(report_fp, "[Truncated – full file larger than snippet]\n");
    fclose(file);
    fprintf(report_fp, "\n");
}

// Recursive function to traverse and report on directories/files
void traverse_dir(const char *base_path, FILE *report_fp, int depth, int is_focus, int fetch_content) {
    DIR *dir;
    struct dirent *entry;
    char path[MAX_PATH];
    struct stat statbuf;

    if (!(dir = opendir(base_path))) {
        fprintf(report_fp, "Error: Could not open directory %s (errno: %d)\n", base_path, errno);
        return;
    }

    while ((entry = readdir(dir)) != NULL) {
        if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0) continue;

        snprintf(path, sizeof(path), "%s/%s", base_path, entry->d_name);

        if (stat(path, &statbuf) == -1) {
            fprintf(report_fp, "Error: Could not stat %s (errno: %d)\n", path, errno);
            continue;
        }

        // Indent based on depth
        for (int i = 0; i < depth; i++) fprintf(report_fp, "  ");

        // File/Folder name and basic info
        time_t mod_time = statbuf.st_mtime;
        char time_str[64];
        strftime(time_str, sizeof(time_str), "%Y-%m-%d %H:%M:%S", localtime(&mod_time));
        fprintf(report_fp, "%s (Size: %ld bytes, Modified: %s) – ", entry->d_name, statbuf.st_size, time_str);

        if (is_directory(path)) {
            fprintf(report_fp, "Directory – Contains sub-files/folders for AI components.\n");
            // Recurse
            traverse_dir(path, report_fp, depth + 1, is_focus, fetch_content);
        } else {
            fprintf(report_fp, "%s\n", get_file_description(entry->d_name));
            if (fetch_content) {
                fetch_file_content(path, report_fp);
            }
        }
    }
    closedir(dir);
}

int main(int argc, char *argv[]) {
    int fetch_content = 0;
    if (argc > 1 && strcmp(argv[1], "--fetch") == 0) {
        fetch_content = 1;
        printf("Fetching content snippets enabled.\n");
    }

    const char *root_dir = "/code";  // Your local code base root
    FILE *report_fp = fopen(REPORT_FILE, "w");
    if (report_fp == NULL) {
        printf("Error: Could not open report file %s (errno: %d)\n", REPORT_FILE, errno);
        return 1;
    }

    fprintf(report_fp, "Code Base Report for Biblical Figure Knowledge AIs + Supports\n");
    fprintf(report_fp, "Generated: %s\n", asctime(localtime(&(time_t){time(NULL)})));
    fprintf(report_fp, "Root: %s\n\n", root_dir);

    // Traverse root, focus on specified projects
    DIR *root;
    struct dirent *entry;
    char path[MAX_PATH];

    if (!(root = opendir(root_dir))) {
        fprintf(report_fp, "Error: Could not open root %s (errno: %d)\n", root_dir, errno);
        fclose(report_fp);
        return 1;
    }

    while ((entry = readdir(root)) != NULL) {
        if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0) continue;

        snprintf(path, sizeof(path), "%s/%s", root_dir, entry->d_name);

        if (is_directory(path)) {
            int is_focus = 0;
            for (int i = 0; focus_projects[i] != NULL; i++) {
                if (strcmp(entry->d_name, focus_projects[i]) == 0) {
                    is_focus = 1;
                    break;
                }
            }

            if (is_focus) {
                fprintf(report_fp, "Focused Project: %s\n", entry->d_name);
                traverse_dir(path, report_fp, 1, is_focus, fetch_content);
                fprintf(report_fp, "\n");
            } else {
                fprintf(report_fp, "Other Project: %s (skipping details, but exists)\n", entry->d_name);
            }
        }
    }

    closedir(root);
    fclose(report_fp);

    printf("Report generated in %s. Open it to view details.\n", REPORT_FILE);
    return 0;
}