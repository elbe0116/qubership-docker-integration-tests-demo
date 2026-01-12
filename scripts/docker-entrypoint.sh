#!/bin/bash

export ROBOT_OPTIONS="--loglevel=info --outputdir output"
export ROBOT_SYSLOG_FILE=./output/syslog.txt
export ROBOT_SYSLOG_LEVEL=DEBUG

# Pytest output directory
export PYTEST_OUTPUT=${PYTEST_OUTPUT:-/opt/pytest/output}

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

create_tags_resolver_array() {
    tags_resolver_script="robot_tags_resolver.py"
    if [[ -n "$TAGS_RESOLVER_SCRIPT" ]]; then
        tags_resolver_script=${TAGS_RESOLVER_SCRIPT}
    fi
    tags_resolver_array=()
    while
        IFS=";"
        read -d ";" line
    do
        tags_resolver_array+=($line)
    done < <(python "${tags_resolver_script}")
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
    pytest_args+=("-v")
    pytest_args+=("--tb=short")
    pytest_args+=("--alluredir=${PYTEST_OUTPUT}/allure-results")
    
    # Handle tags (markers in pytest)
    if [[ -n "$TAGS" ]]; then
        # Convert Robot tags to pytest markers
        # Replace OR with " or " for pytest marker expression
        marker_expr="${TAGS// OR / or }"
        marker_expr="${marker_expr//OR/ or }"
        pytest_args+=("-m" "$marker_expr")
        echo "Running with markers: $marker_expr"
    fi

    # Handle excluded tags
    if [[ ${IS_TAGS_RESOLVER_ENABLED} == "true" ]]; then
        create_tags_resolver_array
        excluded_tags=${tags_resolver_array[0]}
        if [[ -n "$excluded_tags" ]]; then
            # Add excluded tags to marker expression
            excluded_expr="${excluded_tags// OR / or }"
            excluded_expr="${excluded_expr//OR/ or }"
            excluded_expr="${excluded_expr//-e /}"
            if [[ -n "$marker_expr" ]]; then
                pytest_args+=("-m" "$marker_expr and not ($excluded_expr)")
            else
                pytest_args+=("-m" "not ($excluded_expr)")
            fi
            echo "Excluded markers: $excluded_expr"
        fi
    fi

    pytest_args+=("./tests")
    
    echo "🚀 Running pytest with arguments: ${pytest_args[*]}"
    pytest "${pytest_args[@]}"

    pytest_result=$?
    if [[ ${pytest_result} -ne 0 ]]; then
        echo "Pytest process finished with code - ${pytest_result}"
    fi

    if [[ ${STATUS_WRITING_ENABLED} == "true" ]]; then
        if ! python "$status_writing_script" "update"; then
            echo "Can not update status for integration tests"
        fi
    fi
    
    return ${pytest_result}
}

run_robot() {
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

    excluded_tags=""
    if [[ ${IS_TAGS_RESOLVER_ENABLED} == "true" ]]; then
        create_tags_resolver_array
        echo "Included tags: ${TAGS}"
        echo "Excluded tags: ${tags_resolver_array[0]}"
        echo "${tags_resolver_array[1]}" # print all excluded tags with matched reason
        excluded_tags=${tags_resolver_array[0]}
    fi

    robot_args=()
    if [[ -n "$TAGS" ]]; then
        # Split by OR and add each tag as separate -i parameter
        IFS='OR' read -ra tag_array <<< "$TAGS"
        for tag in "${tag_array[@]}"; do
            # Skip empty tags
            if [[ -n "$tag" ]]; then
                robot_args+=("-i" "$tag")
            fi
        done
    fi
    if [[ -n "$excluded_tags" ]]; then
        # Remove the -e flag if it's already present and parse the tags
        if [[ "$excluded_tags" =~ ^-e[[:space:]]+(.*)$ ]]; then
            # Extract tags without -e flag
            tags_only="${BASH_REMATCH[1]}"
            # Split by OR and add each tag as separate -e parameter
            IFS='OR' read -ra excluded_tag_array <<< "$tags_only"
            for tag in "${excluded_tag_array[@]}"; do
                # Skip empty tags
                if [[ -n "$tag" ]]; then
                    robot_args+=("-e" "$tag")
                fi
            done
        else
            # No -e flag present, add it
            # Split by OR and add each tag as separate -e parameter
            IFS='OR' read -ra excluded_tag_array <<< "$excluded_tags"
            for tag in "${excluded_tag_array[@]}"; do
                # Skip empty tags
                if [[ -n "$tag" ]]; then
                    robot_args+=("-e" "$tag")
                fi
            done
        fi
    fi
    robot_args+=("./tests")
    
    # Call adapter-S3-entrypoint.sh with robot arguments
    echo "🚀 Calling adapter-S3-entrypoint.sh with arguments: ${robot_args[*]}"
    ${ROBOT_HOME}/scripts/adapter-S3/adapter-S3-entrypoint.sh "${robot_args[@]}"

    robot_result=$?
    if [[ ${robot_result} -ne 0 ]]; then
        touch ./output/result.txt
        echo "Robot framework process was interrupted with code - ${robot_result}"
    fi

    analyze_result_script="analyze_result.py"
    if [[ ${IS_ANALYZER_RESULT_ENABLED} == "true" ]]; then
        if [[ -n "$ANALYZE_RESULT_SCRIPT" ]]; then
            analyze_result_script=${ANALYZE_RESULT_SCRIPT}
        fi
        python "${analyze_result_script}"
    fi

    if [[ ${STATUS_WRITING_ENABLED} == "true" ]]; then
        if [[ ${IS_ANALYZER_RESULT_ENABLED} != "true" ]]; then
            python "${analyze_result_script}"
        fi

        if ! python "$status_writing_script" "update"; then
            echo "Can not update status for integration tests"
        fi
    fi
}

# Process some known arguments to run integration tests
case $1 in
custom)
    run_custom_script
    ;;
run-pytest)
    # Run pytest with ttyd
    run_pytest
    run_ttyd
    ;;
run-pytest-without-ttyd)
    run_pytest
    ;;
run-robot)
    # To keep backward compatibility with old entrypoint script we run ttyd by default
    run_robot
    run_ttyd
    ;;
run-robot-without-ttyd)
    run_robot
    ;;
run-ttyd)
    run_ttyd
    ;;
esac

# Otherwise just run the specified command
exec "$@"
