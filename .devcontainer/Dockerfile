FROM python:3.11

WORKDIR /workspace

RUN apt-get update && apt-get install -y --no-install-recommends \
    git build-essential sudo && rm -rf /var/lib/apt/lists/*

ARG USER_UID=1000
ARG USER_GID=1000
RUN groupadd --gid $USER_GID devuser \
    && useradd --uid $USER_UID --gid $USER_GID --shell /bin/bash --create-home devuser \
    && echo devuser ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/devuser \
    && chmod 0440 /etc/sudoers.d/devuser

RUN chown -R devuser:devuser /workspace
USER devuser

ENV PATH="/home/devuser/.local/bin:$PATH"
ENV FLASK_APP=microblog.app
ENV FLASK_ENV=development
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

EXPOSE 5000
CMD ["bash"]
