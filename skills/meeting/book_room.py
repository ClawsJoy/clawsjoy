"""预订会议室"""
class BookRoomSkill:
    def execute(self, params):
        room = params.get('room', 'A101')
        start = params.get('start', '')
        end = params.get('end', '')
        attendees = params.get('attendees', [])
        return {
            "success": True,
            "booking_id": f"MTG_{hash(room+start)}",
            "message": f"已预订 {room} {start}-{end}"
        }
skill = BookRoomSkill()
