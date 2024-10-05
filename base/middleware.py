from django.http import Http404

from .bots import BOT_USER_AGENTS


class PrerenderBotMiddleware:
    def __init__(self, get_response):
        self.BOT_USER_AGENTS = BOT_USER_AGENTS  # List of bot user agents
        self.get_response = get_response

    def is_bot(self, user_agent):
        # Check if the user-agent matches any bot
        return any(bot.lower() in user_agent for bot in self.BOT_USER_AGENTS)

    def __call__(self, request):
        if "/prerender" in request.path:
            user_agent = request.META.get("HTTP_USER_AGENT", "")

            # Allow access if user is authenticated and staff
            if request.user.is_authenticated and request.user.is_staff:
                return self.get_response(request)

            # If it's a bot, allow access
            if self.is_bot(user_agent):
                return self.get_response(request)

            # For everyone else, raise 404
            raise Http404("Page not found.")

        # Proceed with normal request processing
        return self.get_response(request)
