def import_history(file_path):
    import ast
    try:
        ret = ast.literal_eval((open(file_path, 'r').readline()))
    except SyntaxError:
        print ("FATAL ERROR: input file broken!")
        return False
    return ret
