def format_schedule(data):
    return '\n'.join(
        f"{item['startTime']}-{item['endTime']}: {item['name']} ({item.get('description', '')})"
        for item in sorted(data, key=lambda x: x['startTime'])
    )
