#!/usr/bin/env python
from __future__ import print_function

import rospy
from std_msgs.msg import String

import threading
import argparse
import json
import os.path
import pathlib2 as pathlib

import google.oauth2.credentials

from google.assistant.library import Assistant
from google.assistant.library.event import EventType
from google.assistant.library.file_helpers import existing_file
from google.assistant.library.device_helpers import register_device

try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError


WARNING_NOT_REGISTERED = """
    This device is not registered. This means you will not be able to use
    Device Actions or see your device in Assistant Settings. In order to
    register this device follow instructions at:
    https://developers.google.com/assistant/sdk/guides/library/python/embed/register-device
"""



pub = rospy.Publisher('assistant_answers', String, queue_size=10)
gassistant = None
def process_event(event):
    """Pretty prints events.
    Prints all events that occur with two spaces between each new
    conversation and a single space between turns of a conversation.
    Args:
        event(event.Event): The current event to process.
    """
    if event.type == EventType.ON_CONVERSATION_TURN_STARTED:
        print()

    print(event)

    if (event.type == EventType.ON_CONVERSATION_TURN_FINISHED and
            event.args and not event.args['with_follow_on_turn']):
        print()

    if(event.type == EventType.ON_RENDER_RESPONSE):
        pub.publish(event.args['text'])

    if event.type == EventType.ON_DEVICE_ACTION:
        for command, params in event.actions:
            print('Do command', command, 'with params', str(params))


def assistant():
    args = {
        'device_model_id': rospy.get_param('device_model_id', None),
        'project_id': rospy.get_param('project_id', None),
        'device_config': os.path.join(
                            os.path.expanduser('~/.config'),
                            'googlesamples-assistant',
                            'device_config_library.json'
                        )
    }
    
    credentials_f = os.path.join(
                        os.path.expanduser('~/.config'),
                        'google-oauthlib-tool',
                        'credentials.json'
                    )

    device_f = os.path.join(
                    os.path.expanduser('~/.config'),
                    'googlesamples-assistant',
                    'device_config_library.json'
                )
    with open(credentials_f, 'r') as f:
        credentials = google.oauth2.credentials.Credentials(token=None,
                                                            **json.load(f))


    device_model_id = None
    last_device_id = None
    try:
        with open(device_f) as f:
            device_config = json.load(f)
            device_model_id = device_config['model_id']
            last_device_id = device_config.get('last_device_id', None)
    except FileNotFoundError:
        pass

    if not args['device_model_id'] and not device_model_id:
        raise Exception('Missing --device-model-id option')

    # Re-register if "device_model_id" is given by the user and it differs
    # from what we previously registered with.
    should_register = (
        args['device_model_id'] and args['device_model_id'] != device_model_id)

    # device_model_id = args.device_model_id or device_model_id

    with Assistant(credentials, device_model_id) as assistant:
        events = assistant.start()
        gassistant = assistant
        device_id = assistant.device_id
        print('device_model_id:', device_model_id)
        print('device_id:', device_id + '\n')

        # Re-register if "device_id" is different from the last "device_id":
        if should_register or (device_id != last_device_id):
            if args['project_id']:
                register_device(args['project_id'], credentials,
                                device_model_id, device_id)
                pathlib.Path(os.path.dirname(args['device_config'])).mkdir(
                    exist_ok=True)
                with open(args['device_config'], 'w') as f:
                    json.dump({
                        'last_device_id': device_id,
                        'model_id': device_model_id,
                    }, f)
            else:
                print(WARNING_NOT_REGISTERED)

        for event in events:
            process_event(event)
            # rospy.spin()


def main():
    rospy.init_node('assistant', anonymous=True)
    print('Google Assistant Ros node')
    print('Version: ' +  Assistant.__version_str__())

    rate = rospy.Rate(10) # 10hz
    a = threading.Thread(target = assistant)
    a.daemon = True
    a.start()
    while not rospy.is_shutdown():
        rospy.spin()
        rate.sleep()
    exit(0)
    

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass