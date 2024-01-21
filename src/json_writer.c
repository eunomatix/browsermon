#include <stdio.h>
#include <string.h>
#include <fcntl.h>

void write_json_entry(int file_descriptor, const char *newJsonObject) {
    FILE *file = fdopen(file_descriptor, "r+");

    if (file == NULL) {
        printf("Error opening file\n");
        return;
    }

    fseek(file, 0, SEEK_END);

    long fileSize = ftell(file);
    if (fileSize > 0) {
        fseek(file, fileSize - 1, SEEK_SET);
        char lastChar;

        do {
            fread(&lastChar, sizeof(char), 1, file);
            fileSize--;
            fseek(file, fileSize - 1, SEEK_SET);
        } while (lastChar != ']' && fileSize > 0);

        fputc(',', file);
    } else {
        // If the file is empty, create the JSON array
        fputs("[", file);
    }

    fputc('\n', file);
    fputs("  ", file);
    fputs(newJsonObject, file);
    fputc('\n', file);

    fputc(']', file);  // Close the JSON array

    fflush(file);  // Flush changes to the file
}
