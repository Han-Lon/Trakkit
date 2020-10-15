import main_execution

# For running locally. Ensure you have set the proper environment variables
# TODO add list of environment variables needed to run locally. Right now, testing in Lambda works best
if __name__ == '__main__':
    main_execution.lambda_handler(event=None, context=None)