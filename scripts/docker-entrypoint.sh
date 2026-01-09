#!/bin/bash

export PYTEST_OPTIONS="--tb=short -v"

if [[ "$READONLY_CONTAINER_FILE_SYSTEM_ENABLED" == "true" ]]; then
    echo "Read-only file system configuration enabled, copying test files from temp directory..."
    TMP_FOLDER_READ_FS="/opt/robot_tmp"
    cp -r "${TMP_FOLDER_READ_FS}/." "${ROBOT_HOME}/"
fi

if [[ "$DEBUG" == true ]]; then
    set -x
    printenv
fi

run_ttyd() {
    if [[ -z "$TTYD_PORT" ]]; then
        TTYD_PORT=8080
    fi

    exec ttyd -p "${TTYD_PORT}" bash
}

run_custom_script() {
    if [[ -n "$CUSTOM_ENTRYPOINT_SCRIPT" ]]; then
        ${CUSTOM_ENTRYPOINT_SCRIPT}
    fi
}

run_pytest() {
    status_writing_script="write_status.py"
    if [[ ${STATUS_WRITING_ENABLED} == "true" ]]; then
        if [[ -n "$WRITE_STATUS_SCRIPT" ]]; then
            status_writing_script=${WRITE_STATUS_SCRIPT}
        fi
        if ! python "$status_writing_script" "in_progress"; then
            echo "Can not set in progress status for integration tests"
        fi
    fi

    if [[ -n "$SERVICE_CHECKER_SCRIPT" ]]; then
        timeout=300
        if [[ -n "$SERVICE_CHECKER_SCRIPT_TIMEOUT" ]]; then
            timeout=${SERVICE_CHECKER_SCRIPT_TIMEOUT}
        fi
        python "${SERVICE_CHECKER_SCRIPT}" "${timeout}"
        if [[ $? -ne 0 ]]; then
            echo "Service is not ready at least $timeout seconds or some exception occurred"
            exit 1
        fi
    fi

    # Build pytest arguments
    pytest_args=()
    
    # Add markers if TAGS is specified (convert to pytest markers)
    if [[ -n "$TAGS" ]]; then
        # Convert Robot-style tags to pytest markers
        # Split by OR and join with " or " for pytest
        IFS='OR' read -ra tag_array <<< "$TAGS"
        marker_expr=""
        for tag in "${tag_array[@]}"; do
            # Skip empty tags and trim whitespace
            tag=$(echo "$tag" | xargs)
            if [[ -n "$tag" ]]; then
                if [[ -n "$marker_expr" ]]; then
                    marker_expr="$marker_expr or $tag"
                else
                    marker_expr="$tag"
                fi
            fi
        done
        if [[ -n "$marker_expr" ]]; then
            pytest_args+=("-m" "$marker_expr")
        fi
    fi

    # Add excluded tags if specified
    if [[ -n "$EXCLUDED_TAGS" ]]; then
        IFS='OR' read -ra excluded_tag_array <<< "$EXCLUDED_TAGS"
        for tag in "${excluded_tag_array[@]}"; do
            tag=$(echo "$tag" | xargs)
            if [[ -n "$tag" ]]; then
                # Append "not tag" to marker expression
                if [[ -n "${pytest_args[*]}" && "${pytest_args[0]}" == "-m" ]]; then
                    pytest_args[1]="${pytest_args[1]} and not $tag"
                else
                    pytest_args+=("-m" "not $tag")
                fi
            fi
        done
    fi

    # Add test path
    pytest_args+=("./tests")
    
    # Call adapter-S3-entrypoint.sh with pytest arguments
    echo "🚀 Calling adapter-S3-entrypoint.sh with arguments: ${pytest_args[*]}"
    ${ROBOT_HOME}/scripts/adapter-S3/adapter-S3-entrypoint.sh "${pytest_args[@]}"

    pytest_result=$?
    if [[ ${pytest_result} -ne 0 ]]; then
        touch ./output/result.txt
        echo "Pytest process was interrupted with code - ${pytest_result}"
    fi

    # Analyze results (if analyze_result.py is adapted for pytest/junit XML)
    analyze_result_script="analyze_result.py"
    if [[ ${IS_ANALYZER_RESULT_ENABLED} == "true" ]]; then
        if [[ -n "$ANALYZE_RESULT_SCRIPT" ]]; then
            analyze_result_script=${ANALYZE_RESULT_SCRIPT}
        fi
        # Note: analyze_result.py may need adaptation for junit.xml format
        python "${analyze_result_script}" 2>/dev/null || echo "⚠️ Result analyzer not available or failed"
    fi

    if [[ ${STATUS_WRITING_ENABLED} == "true" ]]; then
        if [[ ${IS_ANALYZER_RESULT_ENABLED} != "true" ]]; then
            python "${analyze_result_script}" 2>/dev/null || true
        fi

        if ! python "$status_writing_script" "update"; then
            echo "Can not update status for integration tests"
        fi
    fi
}

# Keep backward compatibility - run_robot calls run_pytest for this project
run_robot() {
    echo "⚠️ run_robot is deprecated for pytest project, calling run_pytest instead"
    run_pytest
}

# Process some known arguments to run integration tests
case $1 in
custom)
    run_custom_script
    ;;
run-pytest)
    # Run pytest tests
    run_pytest
    run_ttyd
    ;;
run-pytest-without-ttyd)
    run_pytest
    ;;
run-robot)
    # Backward compatibility - redirect to pytest
    run_pytest
    run_ttyd
    ;;
run-robot-without-ttyd)
    run_pytest
    ;;
run-ttyd)
    run_ttyd
    ;;
esac

# Otherwise just run the specified command
exec "$@"
