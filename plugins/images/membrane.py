#Save spiking:
saveSourceImage(output_firings, '.' + general_config_hash + config_hash + '.png')
for neuron in to_save:
    stims = []
    n = 0
    for n in range(0, general_config.steps):
        if n in config.step_input:
            found = False
            for s in config.step_input[n]:
                if s[0] == neuron:
                    stims.append(s[1])
                    found = True
            if not found:
                stims.append(0)
        else:
            stims.append(0)

    saveRawImage(membraneImage((membrane_output[neuron], stims), title = config.name + ' - neuron ' + str(neuron)),
        '.' + general_config_hash + config_hash + '_membrane' + str(neuron) + '.png')
for neuron in to_save:
    saveRawImage(membraneImage((membrane_output[neuron], stims), close = False, title = config.name),
        '.' + general_config_hash + config_hash + '_membrane' + str(neuron) + '_Mixed.png', close = False)
#TODO: add "angles" (is a list of lists of angles for every sensory neuron)
saveKey(general_config_hash + config_hash + '_angles', angles)
print("Output file is: %s" % (general_config._history_dir + '/' + '.' + general_config_hash + config_hash))
#Show spiking:
showSourceImage("." + general_config_hash + config_hash + '.png')
for neuron in to_save:
    showSourceImage('.' + general_config_hash + config_hash + '_membrane' + str(neuron) + '.png')
